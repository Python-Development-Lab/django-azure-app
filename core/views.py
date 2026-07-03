import json as _json
import urllib.request
import urllib.error
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


@login_required(login_url='/auth/login/')
def home(request):
    """Головна сторінка"""
    return render(request, 'core/home.html', {
        'user': request.user,
    })


def health_check(request):
    """Перевірка стану для Azure"""
    return HttpResponse("OK", status=200)


@login_required(login_url='/auth/login/')
def security_dashboard(request):
    """Security Dashboard — MITRE ATT&CK coverage"""
    data_path = Path(__file__).parent.parent / 'security' / 'mitre' / 'attack_data.json'
    with open(data_path) as f:
        attack_data = _json.load(f)
    return render(request, 'core/security.html', {
        'attack_data': attack_data,
        'attack_data_json': _json.dumps(attack_data),
    })


def _get_cost_data():
    """Запит до Cost Management API через ManagedIdentityCredential"""
    from azure.identity import ManagedIdentityCredential
    credential = ManagedIdentityCredential()
    token = credential.get_token("https://management.azure.com/.default").token
    subscription_id = "23ee341e-dbd1-4904-8bb2-5dde59747b5d"
    url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        "/providers/Microsoft.CostManagement/query?api-version=2023-11-01"
    )
    body = _json.dumps({
        "type": "ActualCost",
        "timeframe": "MonthToDate",
        "dataset": {
            "granularity": "None",
            "aggregation": {
                "totalCost": {"name": "PreTaxCost", "function": "Sum"}
            },
            "grouping": [
                {"type": "Dimension", "name": "ResourceGroupName"}
            ]
        }
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return _json.loads(resp.read())


@login_required(login_url='/auth/login/')
def finops_dashboard(request):
    """FinOps Dashboard — Azure Cost Management"""
    error = None
    costs = []
    total = 0.0

    try:
        data = _get_cost_data()
        rows = data.get("properties", {}).get("rows", [])
        costs = [
            {"resource_group": r[1], "cost": round(r[0], 2), "currency": r[2]}
            for r in rows if r[0] > 0
        ]
        costs.sort(key=lambda x: x["cost"], reverse=True)
        total = round(sum(c["cost"] for c in costs), 2)
    except Exception as e:
        error = str(e)

    from datetime import date
    today = date.today()
    period_from = today.replace(day=1).strftime("%d %b %Y")
    period_to = today.strftime("%d %b %Y")

    return render(request, "core/finops.html", {
        "costs": costs,
        "costs_json": _json.dumps(costs),
        "total": total,
        "error": error,
        "period_from": period_from,
        "period_to": period_to,
        "period_month": today.strftime("%B %Y"),
    })
