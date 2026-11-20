#!/bin/sh

./manage.py migrate
./manage.py init
chown $PUID:$PGID -R /data

crond
exec su-exec $PUID:$PGID \
    /app/runserver.py
