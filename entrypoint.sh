#!/bin/sh

./manage.py init \
&& crond \
&& chown nobody:nobody -R /data \
&& su nobody -s /app/runserver.py
