#!/bin/sh
set -eu

sed "s/@BACKEND_HOST@/${BACKEND_HOST:-app}/g; s/@BACKEND_PORT@/${BACKEND_PORT:-9000}/g" -i /etc/nginx/conf.d/*.conf
awk '$1=="nameserver"{if(l) { l=l ", "} l=l $2} END{print "resolver " l ";"}' /etc/resolv.conf > /etc/nginx/resolver

exec "$@"
