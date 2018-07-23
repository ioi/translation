#!/usr/bin/env bash

while ! timeout 2 bash -c "cat < /dev/null > /dev/tcp/postgres/5432" 2> /dev/null; do
    echo "Waiting for db..."
    sleep 1
done

cd /usr/src/app

fc-cache

echo "Collecting staticfiles"
python3 manage.py collectstatic --noinput

case "$1" in
    nginx)
        echo "Starting nginx"
        exec /usr/sbin/nginx -g 'daemon off;'
        ;;

    *)
        echo "Migrating Models"
        python3 manage.py migrate

        echo "Starting Gunicorn"
        exec /usr/local/bin/gunicorn Translation.wsgi:application -w $GUNICORN_WORKERS -b :8000
        ;;
esac
