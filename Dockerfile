FROM python:3.13-alpine

ARG BUILD_ENV
ARG IMAGE_VERSION

RUN if [ "$BUILD_ENV" = "rex" ]; then echo "Change depends" \
    && pip config set global.index-url https://proxpi.h.rexzhang.com/index/ \
    && pip config set install.trusted-host proxpi.h.rexzhang.com \
    # https://mirrors.tuna.tsinghua.edu.cn/help/alpine/
    && sed -i 's#https\?://dl-cdn.alpinelinux.org/alpine#https://mirrors.tuna.tsinghua.edu.cn/alpine#g' /etc/apk/repositories \
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
    # create non-root user ---
    && apk add --no-cache su-exec \
    # prepare data path --- \
    && mkdir /data \
    && mkdir /data/lexicon_tld_set

COPY ddns_clienter /app/ddns_clienter
COPY manage.py /app
COPY runserver.py /app
COPY entrypoint.sh /app

WORKDIR /app
EXPOSE 8000

ENV PYTHONPATH=/app
ENV TLDEXTRACT_CACHE_PATH=/data/lexicon_tld_set
ENV DJANGO_SETTINGS_MODULE="ddns_clienter.settings"

ENV DEPLOY_STAGE="prd"
ENV DEPLOY_IN_CONTAINER="true"
ENV DATA_PATH="/data"
ENV CONFIG_TOML="/etc/ddns-clienter.toml"
ENV PBULIC_INSIDE_API="true"

ENV SENTRY_DSN=""

# i18n
RUN ./manage.py compilemessages --ignore venv \
    && ./manage.py collectstatic --no-input

CMD /app/entrypoint.sh

LABEL org.opencontainers.image.title="DDNS Clienter"
LABEL org.opencontainers.image.version="$IMAGE_VERSION"
LABEL org.opencontainers.image.authors="Rex Zhang"
LABEL org.opencontainers.image.url="https://hub.docker.com/r/ray1ex/ddns-clienter"
LABEL org.opencontainers.image.source="https://github.com/rexzhang/ddns-clienter"
