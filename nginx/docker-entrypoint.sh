#!/bin/bash
set -eu

sed "s/@BACKEND_HOST@/${BACKEND_HOST:-app}/g; s/@BACKEND_PORT@/${BACKEND_PORT:-8000}/g" -i /etc/nginx/conf.d/*.conf

exec "$@"
