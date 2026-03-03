from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    """Головна сторінка"""
    context = {
        'title': 'Django 6.0 на Azure',
        'message': 'Вітаємо! Ваш Django додаток працює успішно!',
    }
    return render(request, 'core/home.html', context)


def health_check(request):
    """Перевірка стану для Azure"""
    return HttpResponse("OK", status=200)
