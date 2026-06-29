import json
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
        attack_data = json.load(f)
    return render(request, 'core/security.html', {
        'attack_data': attack_data,
        'attack_data_json': json.dumps(attack_data),
    })
