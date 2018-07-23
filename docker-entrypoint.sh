#!/usr/bin/env bash

cd /usr/src/app
export DJANGO_SETTINGS_MODULE=Translation.settings

fc-cache

echo "Collecting staticfiles"
python3 manage.py collectstatic --noinput

case "$1" in
    nginx)
        echo "Starting nginx"
        exec /usr/sbin/nginx -g 'daemon off;'
        ;;

    gunicorn)
        while ! timeout 2 bash -c "cat < /dev/null > /dev/tcp/$DB_HOST/5432" 2> /dev/null; do
            echo "Waiting for db..."
            sleep 1
        done

        echo "Migrating Models"
        python3 manage.py migrate

        echo "Starting Gunicorn"
        exec /usr/local/bin/gunicorn Translation.wsgi:application -w $GUNICORN_WORKERS -b :8000
        ;;

    *)
        exec "$@"
esac
