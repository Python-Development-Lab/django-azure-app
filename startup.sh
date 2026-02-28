#!/bin/bash
echo "=== Django Startup Script ==="

# Перехід до директорії застосунку
cd /home/site/wwwroot

# Активація віртуального середовища Oryx
if [ -d "antenv" ]; then
    source antenv/bin/activate
    echo "Virtual env activated: antenv"
elif [ -d "/home/site/wwwroot/antenv" ]; then
    source /home/site/wwwroot/antenv/bin/activate
    echo "Virtual env activated from full path"
fi

echo "Python: $(which python)"
echo "Python version: $(python --version)"

# Міграції
echo "Running migrations..."
python manage.py migrate --noinput

# Статичні файли
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Запуск Gunicorn
echo "Starting Gunicorn..."
exec gunicorn djangoapp.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 600 \
    --log-level info \
    --access-logfile '-' \
    --error-logfile '-'