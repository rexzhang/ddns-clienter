#!/bin/sh

chown nobody:nobody -R /data
./manage.py migrate
./manage.py init

crond
exec su-exec nobody:nobody \
    /app/runserver.py
