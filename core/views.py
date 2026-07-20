import json as _json
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render


def _get_token():
    from azure.identity import ManagedIdentityCredential
    return ManagedIdentityCredential().get_token(
        "https://management.azure.com/.default"
    ).token


def _cost_query(token, body, cache_key=None, ttl=600):
    if cache_key:
        hit = cache.get(cache_key)
        if hit is not None:
            return hit
    sub = "23ee341e-dbd1-4904-8bb2-5dde59747b5d"
    url = (
        f"https://management.azure.com/subscriptions/{sub}"
        "/providers/Microsoft.CostManagement/query?api-version=2023-11-01"
    )
    req = urllib.request.Request(
        url, data=_json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = _json.loads(resp.read())
    if cache_key:
        cache.set(cache_key, result, ttl)
    return result


def _all_cost_data():
    """Fetch all cost data in one cached bundle — avoids 429 from parallel HTMX"""
    bundle = cache.get("finops_bundle")
    if bundle is not None:
        return bundle
    token = _get_token()

    # 1. Cost by RG
    rg_data = _cost_query(token, {
        "type": "ActualCost", "timeframe": "MonthToDate",
        "dataset": {
            "granularity": "None",
            "aggregation": {"totalCost": {"name": "PreTaxCost", "function": "Sum"}},
            "grouping": [{"type": "Dimension", "name": "ResourceGroupName"}]
        }
    })
    costs = [
        {"resource_group": r[1], "cost": round(r[0], 2), "currency": r[2]}
        for r in rg_data.get("properties", {}).get("rows", []) if r[0] > 0
    ]
    costs.sort(key=lambda x: x["cost"], reverse=True)
    total = round(sum(c["cost"] for c in costs), 2)

    # 2. Daily trend
    daily_data = _cost_query(token, {
        "type": "ActualCost", "timeframe": "MonthToDate",
        "dataset": {
            "granularity": "Daily",
            "aggregation": {"totalCost": {"name": "PreTaxCost", "function": "Sum"}}
        }
    })
    daily = []
    for r in daily_data.get("properties", {}).get("rows", []):
        ds = str(r[1])
        daily.append({"date": f"{ds[6:8]}.{ds[4:6]}", "cost": round(r[0], 2)})

    # 3. RG breakdown
    bd_data = _cost_query(token, {
        "type": "ActualCost", "timeframe": "MonthToDate",
        "dataset": {
            "granularity": "None",
            "aggregation": {"totalCost": {"name": "PreTaxCost", "function": "Sum"}},
            "grouping": [
                {"type": "Dimension", "name": "MeterCategory"},
                {"type": "Dimension", "name": "MeterSubCategory"}
            ],
            "filter": {
                "dimensions": {
                    "name": "ResourceGroupName",
                    "operator": "In",
                    "values": ["rg-django-azure-staging"]
                }
            }
        }
    })
    breakdown = [
        {"service": r[1], "meter": r[2], "cost": round(r[0], 3)}
        for r in bd_data.get("properties", {}).get("rows", []) if r[0] > 0.001
    ]
    breakdown.sort(key=lambda x: x["cost"], reverse=True)

    bundle = {
        "costs": costs, "total": total,
        "daily": daily, "breakdown": breakdown,
    }
    cache.set("finops_bundle", bundle, 600)
    return bundle


def _get_defender_alerts():
    from azure.identity import ManagedIdentityCredential
    token = ManagedIdentityCredential().get_token(
        "https://management.azure.com/.default"
    ).token
    sub = "23ee341e-dbd1-4904-8bb2-5dde59747b5d"
    url = (f"https://management.azure.com/subscriptions/{sub}"
           "/providers/Microsoft.Security/alerts?api-version=2022-01-01")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = _json.loads(resp.read())
    alerts = []
    for a in data.get("value", []):
        p = a.get("properties", {})
        ext = p.get("extendedProperties", {})
        alerts.append({
            "name": p.get("alertDisplayName", ""),
            "severity": p.get("severity", ""),
            "time": p.get("timeGeneratedUtc", "")[:10],
            "status": p.get("status", ""),
            "intent": p.get("intent", ""),
            "source_ip": ext.get("Sample Source IP Addresses", ""),
            "target_uri": ext.get("Sample URIs", ""),
        })
    alerts.sort(key=lambda x: x["time"], reverse=True)
    return alerts


def _get_http_anomalies():
    """Top-5 suspicious HTTP requests from AppServiceHTTPLogs — 4xx/5xx spikes,
    scanner tool signatures, and failed-auth clusters. Uses the same MSI +
    Log Analytics REST pattern as analytics_rum, scoped to Security Reader."""
    query = """
AppServiceHTTPLogs
| where TimeGenerated > ago(24h)
| where ScStatus >= 400
    or CsUriStem !startswith "/static/"
       and UserAgent has_any ("sqlmap", "nikto", "nmap", "masscan", "nessus", "dirbuster")
| summarize
    Requests = count(),
    Statuses = make_set(ScStatus),
    Paths = make_set(CsUriStem, 5),
    UserAgents = make_set(UserAgent, 3)
  by CIp
| order by Requests desc
| take 5
"""
    rows = _log_analytics_query(query)
    anomalies = []
    for r in rows:
        def _parse_dynamic(val):
            if not val:
                return []
            if isinstance(val, str):
                try:
                    val = _json.loads(val)
                except (ValueError, TypeError):
                    return [val]
            return val if isinstance(val, list) else [val]

        statuses = _parse_dynamic(r[2])
        paths = _parse_dynamic(r[3])
        user_agents = [ua for ua in _parse_dynamic(r[4]) if ua]

        anomalies.append({
            "source_ip": r[0],
            "requests": r[1],
            "statuses": ", ".join(str(s) for s in statuses) if statuses else "—",
            "paths": ", ".join(paths) if paths else "—",
            "user_agents": ", ".join(user_agents) if user_agents else "—",
        })
    return anomalies


def _period_ctx():
    today = date.today()
    return {
        "period_from": today.replace(day=1).strftime("%d %b %Y"),
        "period_to": today.strftime("%d %b %Y"),
        "period_month": today.strftime("%B %Y"),
    }


@login_required(login_url='/auth/login/')
def home(request):
    return render(request, 'core/home.html', {'user': request.user})


def health_check(request):
    return HttpResponse("OK", status=200)


# ── Security Dashboard ────────────────────────────────────────────────────────

@login_required(login_url='/auth/login/')
def security_dashboard(request):
    return render(request, 'core/security.html')


@login_required(login_url='/auth/login/')
def security_coverage(request):
    data_path = (
        Path(__file__).parent.parent / 'security' / 'mitre' / 'attack_data.json'
    )
    with open(data_path) as f:
        attack_data = _json.load(f)
    return render(request, 'core/partials/security_coverage.html', {
        'attack_data': attack_data,
        'attack_data_json': _json.dumps(attack_data),
    })


@login_required(login_url='/auth/login/')
def security_alerts(request):
    defender_alerts = []
    defender_error = None
    try:
        defender_alerts = _get_defender_alerts()
    except Exception as e:
        defender_error = str(e)

    http_anomalies = []
    http_anomalies_error = None
    try:
        http_anomalies = _get_http_anomalies()
    except Exception as e:
        http_anomalies_error = str(e)

    return render(request, 'core/partials/security_alerts.html', {
        'defender_alerts': defender_alerts,
        'defender_error': defender_error,
        'http_anomalies': http_anomalies,
        'http_anomalies_error': http_anomalies_error,
    })


# ── FinOps Dashboard ──────────────────────────────────────────────────────────

@login_required(login_url='/auth/login/')
def finops_dashboard(request):
    return render(request, 'core/finops.html', _period_ctx())


@login_required(login_url='/auth/login/')
def finops_summary(request):
    """Single HTMX endpoint — returns all FinOps content at once (avoids 429)"""
    error = None
    costs, total, daily, breakdown = [], 0.0, [], []
    try:
        b = _all_cost_data()
        costs = b["costs"]
        total = b["total"]
        daily = b["daily"]
        breakdown = b["breakdown"]
    except Exception as e:
        error = str(e)
    ctx = _period_ctx()
    ctx.update({
        "costs": costs,
        "costs_json": _json.dumps(costs),
        "total": total,
        "error": error,
        "daily_trend": daily,
        "daily_trend_json": _json.dumps(daily),
        "rg_breakdown": breakdown,
        "rg_breakdown_json": _json.dumps(breakdown),
        "rg_total": round(sum(r["cost"] for r in breakdown), 3),
    })
    return render(request, 'core/partials/finops_all.html', ctx)


@login_required(login_url='/auth/login/')
def finops_rg_summary(request):
    error = None
    costs = []
    try:
        costs = _all_cost_data()["costs"]
    except Exception as e:
        error = str(e)
    return render(request, 'core/partials/finops_rg_summary.html', {
        'costs': costs,
        'costs_json': _json.dumps(costs),
        'error': error,
    })


@login_required(login_url='/auth/login/')
def finops_daily(request):
    error = None
    daily_trend = []
    try:
        daily_trend = _all_cost_data()["daily"]
    except Exception as e:
        error = str(e)
    ctx = _period_ctx()
    ctx.update({
        'daily_trend_json': _json.dumps(daily_trend),
        'daily_trend': daily_trend,
        'error': error,
    })
    return render(request, 'core/partials/finops_daily.html', ctx)


@login_required(login_url='/auth/login/')
def finops_breakdown(request):
    error = None
    rg_breakdown = []
    try:
        rg_breakdown = _all_cost_data()["breakdown"]
    except Exception as e:
        error = str(e)
    return render(request, 'core/partials/finops_breakdown.html', {
        'rg_breakdown': rg_breakdown,
        'rg_breakdown_json': _json.dumps(rg_breakdown),
        'rg_total': round(sum(r["cost"] for r in rg_breakdown), 3),
        'error': error,
    })


def _log_analytics_query(query):
    """Query Log Analytics workspace via MSI"""
    from azure.identity import ManagedIdentityCredential
    credential = ManagedIdentityCredential()
    token = credential.get_token("https://api.loganalytics.io/.default").token
    # law-django-azure-staging workspace customerId
    workspace_id = "040e48a1-6f6e-45c1-abbc-607fa04f16de"
    url = f"https://api.loganalytics.io/v1/workspaces/{workspace_id}/query"
    body = _json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = _json.loads(resp.read())
    return data.get("tables", [{}])[0].get("rows", [])


@login_required(login_url='/auth/login/')
def analytics_dashboard(request):
    return render(request, 'core/analytics.html')


@login_required(login_url='/auth/login/')
def analytics_pageviews(request):
    error = None
    rows = []
    try:
        rows = _log_analytics_query("""
AppPageViews
| where TimeGenerated > ago(24h)
| extend CleanUrl = tostring(split(Url, "?")[0])
| summarize Views=count(), AvgDuration=avg(DurationMs)
  by Name, Url=CleanUrl
| order by Views desc
| take 10
""")
    except Exception as e:
        error = str(e)
    pages = [{"name": r[0], "url": r[1], "views": r[2],
              "avg_ms": round(r[3] or 0)} for r in rows]
    total_views = sum(p["views"] for p in pages)
    return render(request, 'core/partials/analytics_pageviews.html', {
        'pages': pages,
        'total_views': total_views,
        'error': error,
    })


@login_required(login_url='/auth/login/')
def analytics_browsers(request):
    error = None
    browser_data, os_data = [], []
    try:
        browser_data = _log_analytics_query("""
AppPageViews
| where TimeGenerated > ago(24h)
| summarize count() by ClientBrowser
| order by count_ desc | take 8
""")
        os_data = _log_analytics_query("""
AppPageViews
| where TimeGenerated > ago(24h)
| summarize count() by ClientOS
| order by count_ desc | take 6
""")
    except Exception as e:
        error = str(e)
    browsers = [{"name": r[0] or "Unknown", "count": r[1]} for r in browser_data]
    os_list = [{"name": r[0] or "Unknown", "count": r[1]} for r in os_data]
    return render(request, 'core/partials/analytics_browsers.html', {
        'browsers': browsers,
        'os_list': os_list,
        'browsers_json': _json.dumps(browsers),
        'os_json': _json.dumps(os_list),
        'error': error,
    })


@login_required(login_url='/auth/login/')
def analytics_performance(request):
    error = None
    trend = []
    try:
        rows = _log_analytics_query("""
AppPageViews
| where TimeGenerated > ago(24h)
| summarize Views=count(), AvgMs=avg(DurationMs)
  by bin(TimeGenerated, 1h)
| order by TimeGenerated asc
""")
        trend = [{"hour": str(r[0])[:16], "views": r[1],
                  "avg_ms": round(r[2] or 0)} for r in rows]
    except Exception as e:
        error = str(e)
    return render(request, 'core/partials/analytics_performance.html', {
        'trend': trend,
        'trend_json': _json.dumps(trend),
        'error': error,
    })


@login_required(login_url='/auth/login/')
def analytics_rum(request):
    """RUM — Real User Monitoring via AppBrowserTimings"""
    error = None
    metrics = []
    exceptions = []
    try:
        rows = _log_analytics_query(
            "AppBrowserTimings"
            " | where TimeGenerated > ago(24h)"
            " | summarize AvgTotal=avg(TotalDurationMs),"
            " AvgNetwork=avg(NetworkDurationMs),"
            " AvgProcessing=avg(ProcessingDurationMs),"
            " AvgSend=avg(SendDurationMs),"
            " AvgReceive=avg(ReceiveDurationMs),"
            " Count=count() by Name"
            " | order by AvgTotal desc"
        )
        metrics = [{
            "name": r[0],
            "avg_total": round(r[1] or 0),
            "avg_network": round(r[2] or 0),
            "avg_processing": round(r[3] or 0),
            "avg_send": round(r[4] or 0),
            "avg_receive": round(r[5] or 0),
            "count": r[6],
        } for r in rows]

        exc_rows = _log_analytics_query(
            "AppExceptions"
            " | where TimeGenerated > ago(24h)"
            " | summarize count() by ProblemId,"
            " OuterMessage=substring(OuterMessage, 0, 80)"
            " | order by count_ desc | take 5"
        )
        exceptions = [{"id": r[0], "message": r[1], "count": r[2]}
                      for r in exc_rows]
    except Exception as e:
        error = str(e)

    overall_avg = round(sum(m["avg_total"] for m in metrics) / len(metrics)) if metrics else 0

    return render(request, 'core/partials/analytics_rum.html', {
        'metrics': metrics,
        'metrics_json': _json.dumps(metrics),
        'exceptions': exceptions,
        'overall_avg': overall_avg,
        'error': error,
    })
