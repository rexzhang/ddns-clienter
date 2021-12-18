#!/bin/sh

django-admin init \
&& django-admin migrate \
&& django-admin compilemessages --ignore venv \
&& crond \
&& python -m ddns_clienter runserver --host 0.0.0.0 --port 80
