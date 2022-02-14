FROM python:3.10-alpine

ARG ENV

RUN if [ "$ENV" = "rex" ]; then echo "Change depends" \
    && pip config set global.index-url http://192.168.200.21:3141/root/pypi/+simple \
    && pip config set install.trusted-host 192.168.200.21 \
    && sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories \
    ; fi

COPY ddns_clienter /app/ddns_clienter
COPY ddns_clienter_core /app/ddns_clienter_core
COPY requirements /app/requirements
COPY runserver.py /app
COPY entrypoint.sh /app

# depends
RUN \
    # install depends
    pip install --no-cache-dir -r /app/requirements/docker.txt \
    && apk add --no-cache gettext \
    # prepare data path
    && mkdir /data \
    && chown nobody:nobody /data

WORKDIR /app
#VOLUME /data
EXPOSE 8000

ENV PYTHONPATH=/app
ENV DATA_DIR=/data
ENV DJANGO_SETTINGS_MODULE="ddns_clienter.settings"
ENV CONFIG_FILE_NAME="config.toml"
ENV SENTRY_DSN=""

# i18n
RUN django-admin compilemessages --ignore venv

CMD /app/entrypoint.sh

LABEL org.opencontainers.image.title="DDNS Clienter"
LABEL org.opencontainers.image.authors="Rex Zhang"
LABEL org.opencontainers.image.url="https://hub.docker.com/r/ray1ex/ddns-clienter"
LABEL org.opencontainers.image.source="https://github.com/rexzhang/ddns-clienter"