#!/bin/sh

django-admin init \
&& crond \
&& chown nobody:nobody -R /data \
&& su nobody -s /app/runserver.py
