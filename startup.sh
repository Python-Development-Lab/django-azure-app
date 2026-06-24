#!/bin/bash
echo "=== Django startup ==="

cd /home/site/wwwroot
export PYTHONPATH=/home/site/wwwroot/packages

echo "Python version:"
python --version

echo "Running migrations..."
python manage.py migrate --noinput 2>&1 || echo "Migration warning (check logs)"

echo "Starting gunicorn..."
exec gunicorn djangoapp.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --timeout 120 \
  --access-logfile '-' \
  --error-logfile '-'
