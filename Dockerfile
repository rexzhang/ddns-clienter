FROM python:3.10-alpine

# ---------- for develop
RUN pip config set global.index-url http://192.168.200.22:3141/root/pypi/+simple \
    && pip config set install.trusted-host 192.168.200.22
# ----------

COPY ddns_clienter /app/ddns_clienter
COPY ddns_clienter_core /app/ddns_clienter_core
COPY requirements /app/requirements
RUN pip install --no-cache-dir -r /app/requirements/docker.txt

WORKDIR /app
EXPOSE 80
VOLUME /data
ENV PYTHONPATH=/app
ENV DATA_DIR=/data
ENV  DJANGO_SETTINGS_MODULE="ddns_clienter.settings"

CMD django-admin init \
    && python -m ddns_clienter runserver --host 0.0.0.0 --port 80

LABEL org.opencontainers.image.title="DDNS Clienter"
LABEL org.opencontainers.image.authors="Rex Zhang"
LABEL org.opencontainers.image.url="https://hub.docker.com/repository/docker/ray1ex/..."
LABEL org.opencontainers.image.source="https://github.com/rexzhang/ddns-clienter"