import json as _json
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_token():
    from azure.identity import ManagedIdentityCredential
    credential = ManagedIdentityCredential()
    return credential.get_token("https://management.azure.com/.default").token


def _cost_query(token, body):
    subscription_id = "23ee341e-dbd1-4904-8bb2-5dde59747b5d"
    url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        "/providers/Microsoft.CostManagement/query?api-version=2023-11-01"
    )
    req = urllib.request.Request(
        url, data=_json.dumps(body).encode("utf-8"), method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return _json.loads(resp.read())


def _get_cost_by_rg(token):
    return _cost_query(token, {
        "type": "ActualCost", "timeframe": "MonthToDate",
        "dataset": {
            "granularity": "None",
            "aggregation": {"totalCost": {"name": "PreTaxCost", "function": "Sum"}},
            "grouping": [{"type": "Dimension", "name": "ResourceGroupName"}]
        }
    })


def _get_daily_trend(token):
    data = _cost_query(token, {
        "type": "ActualCost", "timeframe": "MonthToDate",
        "dataset": {
            "granularity": "Daily",
            "aggregation": {"totalCost": {"name": "PreTaxCost", "function": "Sum"}}
        }
    })
    rows = data.get("properties", {}).get("rows", [])
    daily = []
    for r in rows:
        date_str = str(r[1])
        label = f"{date_str[6:8]}.{date_str[4:6]}"
        daily.append({"date": label, "cost": round(r[0], 2)})
    return daily


def _get_rg_breakdown(token):
    data = _cost_query(token, {
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
    rows = data.get("properties", {}).get("rows", [])
    breakdown = [
        {"service": r[1], "meter": r[2], "cost": round(r[0], 3)}
        for r in rows if r[0] > 0.001
    ]
    breakdown.sort(key=lambda x: x["cost"], reverse=True)
    return breakdown


def _get_defender_alerts():
    from azure.identity import ManagedIdentityCredential
    credential = ManagedIdentityCredential()
    token = credential.get_token("https://management.azure.com/.default").token
    subscription_id = "23ee341e-dbd1-4904-8bb2-5dde59747b5d"
    url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        "/providers/Microsoft.Security/alerts?api-version=2022-01-01"
    )
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
            "entity": p.get("compromisedEntity", ""),
            "intent": p.get("intent", ""),
            "description": p.get("description", "")[:200],
            "source_ip": ext.get("Sample Source IP Addresses", ""),
            "user_agent": ext.get("Sample User Agents", ""),
            "target_uri": ext.get("Sample URIs", ""),
        })
    alerts.sort(key=lambda x: x["time"], reverse=True)
    return alerts


def _period_ctx():
    today = date.today()
    return {
        "period_from": today.replace(day=1).strftime("%d %b %Y"),
        "period_to": today.strftime("%d %b %Y"),
        "period_month": today.strftime("%B %Y"),
    }


# ── Core views ────────────────────────────────────────────────────────────────

@login_required(login_url='/auth/login/')
def home(request):
    return render(request, 'core/home.html', {'user': request.user})


def health_check(request):
    return HttpResponse("OK", status=200)


# ── Security Dashboard ────────────────────────────────────────────────────────

@login_required(login_url='/auth/login/')
def security_dashboard(request):
    """Shell — loads instantly, HTMX fetches partials"""
    return render(request, 'core/security.html')


@login_required(login_url='/auth/login/')
def security_coverage(request):
    """HTMX partial: ATT&CK graph + coverage matrix"""
    data_path = Path(__file__).parent.parent / 'security' / 'mitre' / 'attack_data.json'
    with open(data_path) as f:
        attack_data = _json.load(f)
    return render(request, 'core/partials/security_coverage.html', {
        'attack_data': attack_data,
        'attack_data_json': _json.dumps(attack_data),
    })


@login_required(login_url='/auth/login/')
def security_alerts(request):
    """HTMX partial: Defender for Cloud alerts"""
    defender_alerts = []
    defender_error = None
    try:
        defender_alerts = _get_defender_alerts()
    except Exception as e:
        defender_error = str(e)
    return render(request, 'core/partials/security_alerts.html', {
        'defender_alerts': defender_alerts,
        'defender_error': defender_error,
    })


# ── FinOps Dashboard ──────────────────────────────────────────────────────────

@login_required(login_url='/auth/login/')
def finops_dashboard(request):
    """Shell — loads instantly, HTMX fetches partials"""
    return render(request, 'core/finops.html', _period_ctx())


@login_required(login_url='/auth/login/')
def finops_summary(request):
    """HTMX partial: 3 summary cards"""
    costs = []
    total = 0.0
    error = None
    try:
        token = _get_token()
        data = _get_cost_by_rg(token)
        rows = data.get("properties", {}).get("rows", [])
        costs = [
            {"resource_group": r[1], "cost": round(r[0], 2), "currency": r[2]}
            for r in rows if r[0] > 0
        ]
        costs.sort(key=lambda x: x["cost"], reverse=True)
        total = round(sum(c["cost"] for c in costs), 2)
    except Exception as e:
        error = str(e)
    ctx = _period_ctx()
    ctx.update({"costs": costs, "total": total, "error": error})
    return render(request, 'core/partials/finops_summary.html', ctx)


@login_required(login_url='/auth/login/')
def finops_rg_summary(request):
    """HTMX partial: bar chart + doughnut by resource group"""
    costs = []
    error = None
    try:
        token = _get_token()
        data = _get_cost_by_rg(token)
        rows = data.get("properties", {}).get("rows", [])
        costs = [
            {"resource_group": r[1], "cost": round(r[0], 2)}
            for r in rows if r[0] > 0
        ]
        costs.sort(key=lambda x: x["cost"], reverse=True)
    except Exception as e:
        error = str(e)
    return render(request, 'core/partials/finops_rg_summary.html', {
        'costs': costs,
        'costs_json': _json.dumps(costs),
        'error': error,
    })


@login_required(login_url='/auth/login/')
def finops_daily(request):
    """HTMX partial: daily spend trend line chart"""
    daily_trend = []
    error = None
    try:
        token = _get_token()
        daily_trend = _get_daily_trend(token)
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
    """HTMX partial: rg-django-azure-staging service breakdown"""
    rg_breakdown = []
    error = None
    try:
        token = _get_token()
        rg_breakdown = _get_rg_breakdown(token)
    except Exception as e:
        error = str(e)
    return render(request, 'core/partials/finops_breakdown.html', {
        'rg_breakdown': rg_breakdown,
        'rg_breakdown_json': _json.dumps(rg_breakdown),
        'rg_total': round(sum(r["cost"] for r in rg_breakdown), 3),
        'error': error,
    })
