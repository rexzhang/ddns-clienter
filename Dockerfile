FROM crp.rexzhang.com/library/python:3.13-alpine

ARG BUILD_DEV
RUN if [ "$BUILD_DEV" = "rex" ]; then echo "Change depends" \
    && pip config set global.index-url https://proxpi.h.rexzhang.com/index/ \
    && pip config set install.trusted-host proxpi.h.rexzhang.com \
    && sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories \
    # && sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
    ; fi

COPY ./requirements.d /app/requirements.d

# depends
RUN \
    # install depends \
    apk add --no-cache --virtual .build-deps build-base libffi-dev \
    # -- for i18n
    && apk add --no-cache gettext \
    # -- for py
    && pip install --no-cache-dir -r /app/requirements.d/docker.txt \
    # cleanup --- \
    && apk del .build-deps \
    && rm -rf /root/.cache \
    && find /usr/local/lib/python*/ -type f -name '*.py[cod]' -delete \
    && find /usr/local/lib/python*/ -type d -name "__pycache__" -delete \
    # prepare data path --- \
    && mkdir /data \
    && mkdir /data/lexicon_tld_set \
    && chown nobody:nobody -R /data

COPY ddns_clienter /app/ddns_clienter
COPY ddns_clienter_core /app/ddns_clienter_core
COPY manage.py /app
COPY runserver.py /app
COPY entrypoint.sh /app

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
