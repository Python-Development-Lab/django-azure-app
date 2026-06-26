import logging
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)


@login_required(login_url='/auth/login/')
def home(request):
    """Головна сторінка"""
    return render(request, 'core/home.html', {
        'user': request.user,
    })


def health_check(request):
    """Перевірка стану для Azure"""
    logger.warning("Health check called — OpenTelemetry test")
    return HttpResponse("OK", status=200)
