#!/bin/sh

./manage.py migrate
./manage.py init
chown nobody:nobody -R /data

crond
exec su-exec nobody:nobody \
    /app/runserver.py
