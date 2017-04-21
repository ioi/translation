#!/usr/bin/env bash

cd /usr/src/app

echo "Collecting staticfiles"
python manage.py collectstatic --noinput

echo "Migrating Models"
python manage.py migrate

echo "Starting Gunicorn"
/usr/local/bin/gunicorn IOI.wsgi:application -w 1 -b :8000