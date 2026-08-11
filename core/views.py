import json as _json
import logging
import time
import urllib.request
import urllib.error
from datetime import date, timedelta
from datetime import datetime as _datetime_cls
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .services import (
    _sync_cost_export_if_stale,
    _resource_costs_from_db,
    _monthly_trend_from_db,
    _daily_and_rg_costs_from_db,
)


logger = logging.getLogger(__name__)


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


def _month_bounds(year=None, month=None):
    """Return (year, month, first_date, last_date) for the given or current month."""
    today = date.today()
    if year and month:
        first = date(year, month, 1)
    else:
        first = today.replace(day=1)
        year, month = first.year, first.month
    if year == today.year and month == today.month:
        last = today
    else:
        if month == 12:
            last = date(year, 12, 31)
        else:
            last = date(year, month + 1, 1) - timedelta(days=1)
    return year, month, first, last


def _live_costs_and_daily(token, time_period):
    # 1. Cost by RG
    rg_data = _cost_query(token, {
        "type": "ActualCost", "timeframe": "Custom", "timePeriod": time_period,
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

    # 2. Daily trend, grouped by ResourceGroupName -- one query serves both the
    #    combined "All" series and the per-RG series for the dropdown selector,
    #    instead of two separate Cost Management calls.
    daily_rg_data = _cost_query(token, {
        "type": "ActualCost", "timeframe": "Custom", "timePeriod": time_period,
        "dataset": {
            "granularity": "Daily",
            "aggregation": {"totalCost": {"name": "PreTaxCost", "function": "Sum"}},
            "grouping": [{"type": "Dimension", "name": "ResourceGroupName"}]
        }
    })
    daily_cols = [c.get("name") for c in daily_rg_data.get("properties", {}).get("columns", [])]

    def _col_idx(cols, *names):
        for n in names:
            if n in cols:
                return cols.index(n)
        return None

    idx_cost = _col_idx(daily_cols, "PreTaxCost", "Cost")
    idx_date = _col_idx(daily_cols, "UsageDate")
    idx_rg = _col_idx(daily_cols, "ResourceGroupName")

    daily = []
    daily_by_rg = {}
    if idx_cost is not None and idx_date is not None and idx_rg is not None:
        totals, per_rg, raw_dates = {}, {}, set()
        for r in daily_rg_data.get("properties", {}).get("rows", []):
            cost = r[idx_cost]
            ds = str(r[idx_date])
            rg = r[idx_rg]
            lbl = f"{ds[6:8]}.{ds[4:6]}"
            raw_dates.add(ds)
            totals[lbl] = totals.get(lbl, 0) + cost
            per_rg.setdefault(rg, {})
            per_rg[rg][lbl] = per_rg[rg].get(lbl, 0) + cost
        sorted_dates = sorted(raw_dates)
        daily_labels = [f"{d[6:8]}.{d[4:6]}" for d in sorted_dates]
        daily = [{"date": lbl, "cost": round(totals.get(lbl, 0), 2)} for lbl in daily_labels]
        daily_by_rg = {
            rg: [round(per_rg.get(rg, {}).get(lbl, 0), 2) for lbl in daily_labels]
            for rg in per_rg
        }
    else:
        logger.warning(
            "finops: unexpected columns in daily-by-RG response (%s), "
            "falling back to ungrouped daily query" % (daily_cols,)
        )
        daily_data = _cost_query(token, {
            "type": "ActualCost", "timeframe": "Custom", "timePeriod": time_period,
            "dataset": {
                "granularity": "Daily",
                "aggregation": {"totalCost": {"name": "PreTaxCost", "function": "Sum"}}
            }
        })
        for r in daily_data.get("properties", {}).get("rows", []):
            ds = str(r[1])
            daily.append({"date": f"{ds[6:8]}.{ds[4:6]}", "cost": round(r[0], 2)})

    return costs, total, daily, daily_by_rg


def _all_cost_data(year=None, month=None):
    """Fetch all cost data in one cached bundle — avoids 429 from parallel HTMX"""
    year, month, first, last = _month_bounds(year, month)
    bundle_key = f"finops_bundle:{year:04d}-{month:02d}"
    bundle = cache.get(bundle_key)
    if bundle is not None:
        return bundle
    db_result = _daily_and_rg_costs_from_db(year, month)
    token = _get_token()
    time_period = {"from": first.strftime("%Y-%m-%d"), "to": last.strftime("%Y-%m-%d")}

    if db_result is not None:
        costs = db_result["costs"]
        total = db_result["total"]
        daily = db_result["daily"]
        daily_by_rg = db_result["daily_by_rg"]
    else:
        costs, total, daily, daily_by_rg = _live_costs_and_daily(token, time_period)
    # 3. RG breakdown -- ALWAYS live API, no DB fallback (CostRecord doesn't
    # store MeterCategory/MeterSubCategory, only ResourceId/RG/date/cost).
    # Per AI PR Review on PR #46 (11.08.2026): this means the 429 banner
    # can still appear for the breakdown section even on months where
    # Total/Daily Spend Trend are already correctly DB-backed and 429-free
    # -- the DB-first fix only covers costs/total/daily/daily_by_rg, not
    # this section. Known, accepted interim state; a full fix would mean
    # extending the Cost Management export's column configuration to
    # include MeterCategory/MeterSubCategory and re-syncing CostRecord,
    # tracked as a separate backlog item rather than folded into this fix.
    # 3. RG breakdown
    bd_data = _cost_query(token, {
        "type": "ActualCost", "timeframe": "Custom", "timePeriod": time_period,
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
        "daily": daily, "daily_by_rg": daily_by_rg, "breakdown": breakdown,
    }
    cache.set(bundle_key, bundle, 600)
    return bundle


_COST_MGMT_MAX_RETRIES = 2
_COST_MGMT_DEFAULT_RETRY_S = 20
_COST_MGMT_MAX_RETRY_S = 30
# NOTE: this sleep runs on the actual synchronous Django request thread
# (no background/async execution in this file) -- it is bounded (max
# _COST_MGMT_MAX_RETRIES retries, capped at _COST_MGMT_MAX_RETRY_S each)
# and only fires on a real 429 during a cold-cache-population event, not
# on every request. If this code is ever moved behind an async view or a
# background task, this comment -- and the trade-off it documents -- can
# be revisited.


def _retry_on_429(fn):
    """Call fn(); on HTTP 429 from Cost Management, sleep for the duration
    the server itself reports (Retry-After header, per the documented QPU
    throttling contract in Microsoft Learn "Manage Azure costs with
    automation": x-ms-ratelimit-microsoft.costmanagement-qpu-retry-after)
    and retry, instead of a fixed pre-emptive delay. No delay at all when
    the rate-limit window has already cleared; a bounded, server-directed
    wait when it has not. Only retries actual 429s -- any other error
    propagates immediately.
    """
    last_exc = None
    for attempt in range(_COST_MGMT_MAX_RETRIES + 1):
        try:
            return fn()
        except urllib.error.HTTPError as e:
            last_exc = e
            if e.code != 429:
                raise
            if attempt == _COST_MGMT_MAX_RETRIES:
                break
            retry_after = e.headers.get("Retry-After") or e.headers.get(
                "x-ms-ratelimit-microsoft.costmanagement-qpu-retry-after"
            )
            try:
                wait_s = min(float(retry_after), _COST_MGMT_MAX_RETRY_S)
            except (TypeError, ValueError):
                # Cost Management documents delta-seconds for this header,
                # not an HTTP-date string, but fall back safely either way
                # and log which path was used for observability.
                wait_s = _COST_MGMT_DEFAULT_RETRY_S
                logger.warning(
                    "finops: Retry-After header missing or unparseable (%r), using default %ds"
                    % (retry_after, _COST_MGMT_DEFAULT_RETRY_S)
                )
            logger.warning(
                "finops: 429 from Cost Management, retrying in %.0fs (attempt %d/%d)"
                % (wait_s, attempt + 1, _COST_MGMT_MAX_RETRIES)
            )
            time.sleep(wait_s)
    raise last_exc


def _monthly_and_resource_data(year=None, month=None):
    """Monthly trend + per-resource breakdown, computed together under ONE
    shared cache entry -- fixes the original cross-worker 429 race without
    adding load to the three legacy endpoints that only need items 1-3.
    """
    year, month, _first, _last = _month_bounds(year, month)
    cache_key = f"finops_extra:{year:04d}-{month:02d}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    # Runs synchronously in this request's path (no Celery/background task
    # infra in this project). Cold-path cost: on the first uncached request
    # per worker per day, this blocks briefly on a Blob Storage download +
    # CSV parse before continuing. Every other request today hits the
    # in-memory cache above and never reaches this line. Per AI PR Review
    # feedback -- noted here explicitly rather than only in services.py,
    # since this is the actual call site on the request path.
    try:
        _sync_cost_export_if_stale(year, month)
    except Exception:
        logger.exception("finops: _sync_cost_export_if_stale failed")

    token = _get_token()

    monthly_trend = None
    try:
        monthly_trend = _monthly_trend_from_db(12)
    except Exception:
        logger.exception("finops: _monthly_trend_from_db failed")
    if monthly_trend is None:
        monthly_trend = []
        try:
            monthly_trend = _retry_on_429(lambda: _monthly_trend(12, token=token))
        except Exception:
            logger.exception("finops: _monthly_trend(12) failed")

    resource_costs = None
    try:
        resource_costs = _resource_costs_from_db(year, month)
    except Exception:
        logger.exception("finops: _resource_costs_from_db failed")
    if resource_costs is None:
        resource_costs = {"resources": [], "top": [], "total": 0.0}
        try:
            resource_costs = _retry_on_429(lambda: _resource_costs(year, month, token=token))
        except Exception:
            logger.exception("finops: _resource_costs failed")
    result = {"monthly_trend": monthly_trend, "resource_costs": resource_costs}
    cache.set(cache_key, result, 900)
    return result


def _month_options(count=12):
    """Last `count` months (most recent first) as {value, label} for a dropdown."""
    today = date.today()
    options = []
    y, m = today.year, today.month
    for _ in range(count):
        options.append({
            "value": f"{y:04d}-{m:02d}",
            "label": date(y, m, 1).strftime("%B %Y"),
        })
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return options


def _monthly_trend(months=12, token=None):
    """Total cost per month for the last `months` months (oldest first)."""
    cache_key = f"finops_monthly_trend_{months}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    today = date.today()
    y, m = today.year, today.month
    for _ in range(months - 1):
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    start = date(y, m, 1)
    token = token or _get_token()
    data = _cost_query(token, {
        "type": "ActualCost", "timeframe": "Custom",
        "timePeriod": {
            "from": start.strftime("%Y-%m-%d"),
            "to": today.strftime("%Y-%m-%d"),
        },
        "dataset": {
            "granularity": "Monthly",
            "aggregation": {"totalCost": {"name": "PreTaxCost", "function": "Sum"}}
        }
    })
    trend = []
    rows = data.get("properties", {}).get("rows", [])
    if rows:
        logger.info("finops: _monthly_trend raw row sample: %s" % (rows[0],))
    for r in rows:
        ds = str(r[1])
        y2, m2 = int(ds[0:4]), int(ds[4:6])
        trend.append({
            "month": f"{y2:04d}-{m2:02d}",
            "label": date(y2, m2, 1).strftime("%b %Y"),
            "cost": round(r[0], 2),
        })
    trend.sort(key=lambda x: x["month"])
    cache.set(cache_key, trend, 3600)
    return trend


def _resource_costs(year=None, month=None, top_n=15, token=None):
    """Cost per individual resource across all resource groups (all-time-in-month)."""
    year, month, first, last = _month_bounds(year, month)
    cache_key = f"finops_resources:{year:04d}-{month:02d}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    token = token or _get_token()
    data = _cost_query(token, {
        "type": "ActualCost", "timeframe": "Custom",
        "timePeriod": {
            "from": first.strftime("%Y-%m-%d"),
            "to": last.strftime("%Y-%m-%d"),
        },
        "dataset": {
            "granularity": "None",
            "aggregation": {"totalCost": {"name": "PreTaxCost", "function": "Sum"}},
            "grouping": [{"type": "Dimension", "name": "ResourceId"}]
        }
    })
    resources = []
    for r in data.get("properties", {}).get("rows", []):
        cost = r[0]
        resource_id = str(r[1] or "")
        if cost <= 0 or not resource_id:
            continue
        parts = resource_id.split("/")
        name = parts[-1] if parts else resource_id
        rg = ""
        lower_parts = [p.lower() for p in parts]
        if "resourcegroups" in lower_parts:
            idx = lower_parts.index("resourcegroups")
            if idx + 1 < len(parts):
                rg = parts[idx + 1]
        resources.append({
            "resource": name,
            "resource_group": rg,
            "cost": round(cost, 3),
        })
    resources.sort(key=lambda x: x["cost"], reverse=True)
    total = round(sum(r["cost"] for r in resources), 2)
    result = {"resources": resources, "top": resources[:top_n], "total": total}
    cache.set(cache_key, result, 3600)
    return result


def _parse_month_param(request):
    """Parse ?month=YYYY-MM from the request. Returns (year, month) or (None, None).
    Falls back to (None, None) -- meaning current month -- on any invalid input,
    including out-of-range months (e.g. ?month=2099-13)."""
    raw = request.GET.get("month")
    if raw:
        try:
            y_str, m_str = raw.split("-")
            year, month = int(y_str), int(m_str)
            if 1 <= month <= 12 and 2000 <= year <= 2100:
                return year, month
        except (ValueError, AttributeError):
            pass
    return None, None


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


def _get_threat_intel_data():
    """Threat Intelligence summary from MDTI connector (ThreatIntelIndicators).
    Uses the same MSI + Log Analytics REST pattern as _get_http_anomalies."""

    summary_rows = []
    recent_rows = []
    error = None

    try:
        summary_rows = _log_analytics_query("""
ThreatIntelIndicators
| where TimeGenerated > ago(7d)
| where IsActive == true
| summarize count() by ObservableKey
| order by count_ desc
""")

        recent_rows = _log_analytics_query("""
ThreatIntelIndicators
| where TimeGenerated > ago(7d)
| where IsActive == true
| project TimeGenerated, ObservableKey, ObservableValue, Confidence, Data
| top 10 by TimeGenerated desc
""")
    except Exception as e:
        error = f"Threat Intelligence query failed: {e}"

    breakdown = []
    total_count = 0
    for row in summary_rows:
        observable_key, count = row[0], row[1]
        breakdown.append({"type": observable_key, "count": count})
        total_count += count

    recent_indicators = []
    for row in recent_rows:
        time_generated_raw, obs_key, obs_value, confidence, data_raw = row
        try:
            if isinstance(time_generated_raw, str):
                time_generated = _datetime_cls.fromisoformat(
                    time_generated_raw.replace("Z", "+00:00")
                )
            else:
                time_generated = time_generated_raw
        except (ValueError, AttributeError):
            time_generated = None
        description = ""
        if data_raw:
            try:
                data_parsed = _json.loads(data_raw) if isinstance(data_raw, str) else data_raw
                description = data_parsed.get("description", "")
            except (ValueError, TypeError, AttributeError):
                description = ""
        recent_indicators.append({
            "time_generated": time_generated,
            "observable_key": obs_key,
            "observable_value": obs_value,
            "confidence": confidence,
            "description": description[:120],
        })

    return {
        "total_count": total_count,
        "breakdown": breakdown,
        "recent_indicators": recent_indicators,
        "error": error,
    }


def _get_traffic_geo():
    """Aggregate request counts by geographic location (24h) using
    geo_info_from_ip_address() — no external GeoIP service needed."""
    query = """
AppServiceHTTPLogs
| where TimeGenerated > ago(24h)
| extend geo = geo_info_from_ip_address(CIp)
| extend Country = tostring(geo.country), City = tostring(geo.city),
         Lat = todouble(geo.latitude), Lon = todouble(geo.longitude)
| where isnotempty(Country) and isnotnull(Lat) and isnotnull(Lon)
| summarize Requests = count(), ErrorCount = countif(ScStatus >= 400)
  by Country, City, Lat, Lon
| order by Requests desc
"""
    rows = _log_analytics_query(query)
    points = []
    for r in rows:
        points.append({
            "country": r[0],
            "city": r[1],
            "lat": r[2],
            "lon": r[3],
            "requests": r[4],
            "errors": r[5],
        })
    return points


def _period_ctx(year=None, month=None):
    today = date.today()
    year, month, first, last = _month_bounds(year, month)
    prev_ref = first - timedelta(days=1)
    next_ref = (date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1))
    is_current_month = (year == today.year and month == today.month)
    return {
        "period_from": first.strftime("%d %b %Y"),
        "period_to": last.strftime("%d %b %Y"),
        "period_month": first.strftime("%B %Y"),
        "selected_month_value": f"{year:04d}-{month:02d}",
        "prev_month_value": f"{prev_ref.year:04d}-{prev_ref.month:02d}",
        "next_month_value": f"{next_ref.year:04d}-{next_ref.month:02d}",
        "is_current_month": is_current_month,
        "month_options": _month_options(12),
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
def security_geo(request):
    return render(request, 'core/partials/security_geo.html', {})


@login_required(login_url='/auth/login/')
def security_geo_data(request):
    try:
        points = _get_traffic_geo()
        return JsonResponse({"points": points, "error": None})
    except Exception as e:
        return JsonResponse({"points": [], "error": str(e)})


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


def security_threat_intel(request):
    context = _get_threat_intel_data()
    return render(request, 'core/partials/security_threat_intel.html', context)


def _parse_compliance_file(file_path):
    """Parses a single compliance .md file: frontmatter (control_id,
    regulation, title, status, date) + '## Description' / '## Evidence' /
    optional '## Gaps' sections."""
    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None

    frontmatter_raw, body = parts[1], parts[2]

    meta = {}
    for line in frontmatter_raw.strip().splitlines():
        if ':' not in line:
            continue
        key, _, value = line.partition(':')
        meta[key.strip()] = value.strip()

    sections = {}
    current_key = None
    current_lines = []
    for line in body.splitlines():
        if line.startswith('## '):
            if current_key:
                sections[current_key] = '\n'.join(current_lines).strip()
            current_key = line[3:].strip()
            current_lines = []
        elif current_key:
            current_lines.append(line)
    if current_key:
        sections[current_key] = '\n'.join(current_lines).strip()

    return {
        'control_id': meta.get('control_id', ''),
        'regulation': meta.get('regulation', ''),
        'title': meta.get('title', file_path.stem),
        'status': meta.get('status', 'unknown'),
        'date': meta.get('date', ''),
        'description': sections.get('Description', ''),
        'evidence': sections.get('Evidence', ''),
        'gaps': sections.get('Gaps', ''),
    }


def _get_compliance_mappings():
    """Scans docs/compliance/*.md, parses each file, sorted by filename."""
    compliance_dir = Path(__file__).parent.parent / 'docs' / 'compliance'
    mappings = []
    error = None

    try:
        if not compliance_dir.exists():
            return [], f"Directory {compliance_dir} not found"

        md_files = sorted(compliance_dir.glob('*.md'))
        for file_path in md_files:
            parsed = _parse_compliance_file(file_path)
            if parsed:
                mappings.append(parsed)
    except Exception as e:
        error = f"Error reading compliance files: {e}"

    return mappings, error


def security_compliance(request):
    """HTMX partial — GET /security/compliance/"""
    mappings, error = _get_compliance_mappings()

    total = len(mappings)
    implemented = sum(1 for m in mappings if m['status'] == 'implemented')
    partial = sum(1 for m in mappings if m['status'] == 'partial')

    return render(request, 'core/partials/security_compliance.html', {
        'mappings': mappings,
        'error': error,
        'total_controls': total,
        'implemented_count': implemented,
        'partial_count': partial,
    })


# ── FinOps Dashboard ──────────────────────────────────────────────────────────

@login_required(login_url='/auth/login/')
def finops_dashboard(request):
    year, month = _parse_month_param(request)
    return render(request, 'core/finops.html', _period_ctx(year, month))


@login_required(login_url='/auth/login/')
def finops_summary(request):
    """Single HTMX endpoint — returns all FinOps content at once (avoids 429)"""
    year, month = _parse_month_param(request)
    error = None
    costs, total, daily, daily_by_rg, breakdown = [], 0.0, [], {}, []
    monthly_trend = []
    resource_costs = {"resources": [], "top": [], "total": 0.0}
    try:
        b = _all_cost_data(year, month)
        costs = b["costs"]
        total = b["total"]
        daily = b["daily"]
        daily_by_rg = b.get("daily_by_rg", {})
        breakdown = b["breakdown"]
    except Exception as e:
        error = str(e)
    # Isolated from the main bundle on purpose: a failure here should not
    # blank out the rest of the dashboard, which already has its own data
    # by now. See _monthly_and_resource_data() for why this is a separate
    # cache entry rather than folded into _all_cost_data().
    try:
        extra = _monthly_and_resource_data(year, month)
        monthly_trend = extra["monthly_trend"]
        resource_costs = extra["resource_costs"]
    except Exception:
        logger.exception("finops: _monthly_and_resource_data failed")
    ctx = _period_ctx(year, month)
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
        "monthly_trend": monthly_trend,
        "monthly_trend_json": _json.dumps(monthly_trend),
        "daily_by_rg_json": _json.dumps(daily_by_rg),
        "resource_costs": resource_costs["resources"],
        "resource_costs_json": _json.dumps(resource_costs["resources"]),
        "resource_top_json": _json.dumps(resource_costs["top"]),
        "resource_total": resource_costs["total"],
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
