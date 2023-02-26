FROM python:3.11-alpine

ARG ENV

RUN if [ "$ENV" = "rex" ]; then echo "Change depends" \
    && pip config set global.index-url http://192.168.200.61:13141/root/pypi/+simple \
    && pip config set install.trusted-host 192.168.200.61 \
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
    # install depends \
    # -- for dns-lexicon
    apk add --no-cache py3-cryptography \
    # -- for i18n
    apk add --no-cache gettext py3-cryptography \
    && pip install --no-cache-dir -r /app/requirements/docker.txt \
    # cleanup ---
    && apk del .build-deps \
    && rm -rf /root/.cache \
    && find /usr/local/lib/python*/ -type f -name '*.py[cod]' -delete \
    && find /usr/local/lib/python*/ -type d -name "__pycache__" -delete \
    # prepare data path
    && mkdir /data \
    && chown nobody:nobody /data

WORKDIR /app
EXPOSE 8000

ENV PYTHONPATH=/app
ENV DATA_DIR=/data
ENV DJANGO_SETTINGS_MODULE="ddns_clienter.settings"
ENV SENTRY_DSN=""
ENV WORK_IN_CONTAINER="true"
ENV LEXICON_TLDEXTRACT_CACHE=/tmp

# i18n
RUN django-admin compilemessages --ignore venv

CMD /app/entrypoint.sh

LABEL org.opencontainers.image.title="DDNS Clienter"
LABEL org.opencontainers.image.authors="Rex Zhang"
LABEL org.opencontainers.image.url="https://hub.docker.com/r/ray1ex/ddns-clienter"
LABEL org.opencontainers.image.source="https://github.com/rexzhang/ddns-clienter"