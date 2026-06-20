#!/bin/bash
cd /home/site/wwwroot
export PYTHONPATH="/home/site/wwwroot/packages:$PYTHONPATH"
exec gunicorn djangoapp.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --log-level info \
    --access-logfile '-' \
    --error-logfile '-'
