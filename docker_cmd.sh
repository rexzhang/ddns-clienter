#!/bin/sh

django-admin init \
&& crond \
&& python -m ddns_clienter runserver --host 0.0.0.0 --port 80
