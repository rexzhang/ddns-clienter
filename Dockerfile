FROM python:3.12-alpine

ARG ENV

RUN if [ "$ENV" = "rex" ]; then echo "Change depends" \
    && pip config set global.index-url http://192.168.200.26:13141/root/pypi/+simple \
    && pip config set install.trusted-host 192.168.200.26 \
    && sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories \
    ; fi

COPY ddns_clienter /app/ddns_clienter
COPY ddns_clienter_core /app/ddns_clienter_core
COPY requirements /app/requirements
COPY manage.py /app
COPY runserver.py /app
COPY entrypoint.sh /app

# depends
RUN \
    # install depends \
    apk add --no-cache --virtual .build-deps build-base libffi-dev \
    # -- for i18n
    && apk add --no-cache gettext \
    # -- for py
    && pip install --no-cache-dir -r /app/requirements/docker.txt \
    # cleanup --- \
    && apk del .build-deps \
    && rm -rf /root/.cache \
    && find /usr/local/lib/python*/ -type f -name '*.py[cod]' -delete \
    && find /usr/local/lib/python*/ -type d -name "__pycache__" -delete \
    # prepare data path --- \
    && mkdir /data \
    && mkdir /data/lexicon_tld_set \
    && chown nobody:nobody -R /data

WORKDIR /app
EXPOSE 8000

ENV PYTHONPATH=/app
ENV TLDEXTRACT_CACHE_PATH=/data/lexicon_tld_set
ENV DJANGO_SETTINGS_MODULE="ddns_clienter.settings"

ENV DATA_PATH="/data"
ENV CONFIG_TOML="/etc/ddns-clienter.toml"
ENV PBULIC_INSIDE_API="true"
ENV WORK_IN_CONTAINER="true"

ENV SENTRY_DSN=""

# i18n
RUN ./manage.py compilemessages --ignore venv \
    && ./manage.py collectstatic --no-input

CMD /app/entrypoint.sh

LABEL org.opencontainers.image.title="DDNS Clienter"
LABEL org.opencontainers.image.authors="Rex Zhang"
LABEL org.opencontainers.image.url="https://hub.docker.com/r/ray1ex/ddns-clienter"
LABEL org.opencontainers.image.source="https://github.com/rexzhang/ddns-clienter"
