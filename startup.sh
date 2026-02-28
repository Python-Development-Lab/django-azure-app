#!/bin/bash

# Активація міграцій
python manage.py migrate --noinput

# Збір статичних файлів
python manage.py collectstatic --noinput

# Запуск Gunicorn
gunicorn djangoapp.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile '-' \
    --error-logfile '-'