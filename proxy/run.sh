#!/bin/sh
set -e

# 'app' 서비스가 시작되기를 기다립니다.
until nc -z $APP_HOST $APP_PORT; do
    echo "Waiting for the 'app' service..."
    sleep 1
done

echo "'app' service is up - executing command"
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
nginx -g 'daemon off;'