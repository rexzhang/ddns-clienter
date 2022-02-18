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
COPY cargo.config.toml /app

# depends
RUN \
    # install depends
    apk add --no-cache --virtual .build-deps build-base musl-dev python3-dev libffi-dev openssl-dev libxml2-dev libxslt-dev cargo ; \
    if [ "$ENV" = "rex" ]; then echo "Change depends" \
    && mkdir /root/.cargo && cp /app/cargo.config.toml /root/.cargo/config.toml \
    ; fi \
    && pip install --no-cache-dir -r /app/requirements/docker.txt \
    && apk del .build-deps \
    && rm -rf /root/.cargo \
    && find /usr/local/lib/python*/ -type f -name '*.py[cod]' -delete \
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
ENV SENTRY_DSN=""
ENV WORK_IN_CONTAINER="true"

# i18n
RUN django-admin compilemessages --ignore venv

CMD /app/entrypoint.sh

LABEL org.opencontainers.image.title="DDNS Clienter"
LABEL org.opencontainers.image.authors="Rex Zhang"
LABEL org.opencontainers.image.url="https://hub.docker.com/r/ray1ex/ddns-clienter"
LABEL org.opencontainers.image.source="https://github.com/rexzhang/ddns-clienter"