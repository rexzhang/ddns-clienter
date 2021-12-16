"""
Django settings for ddns_clienter project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from os import getenv
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DATA_DIR = Path(getenv("DATA_DIR", BASE_DIR))

# Load .env
load_dotenv(BASE_DATA_DIR.joinpath(".env"), override=True)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-mamh*np-ny)gqurc^wup8z_ee^kp@nwvq5$@f-%87qk54he&x$"

# SECURITY WARNING: don't run with debug turned on in production!
if (getenv("DEBUG") is not None) and (getenv("DEBUG").lower() == "true"):
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    # "django.contrib.auth",
    # "django.contrib.contenttypes",
    # "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_bootstrap5",
    "fontawesomefree",
    "ddns_clienter_core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ddns_clienter.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                # "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ddns_clienter.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DATA_DIR.joinpath("db.sqlite3"),
        # "NAME": ":memory:",
    }
}

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = getenv("TZ", "UTC")

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR.joinpath("ddns_clienter", "staticfiles")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# https://docs.djangoproject.com/zh-hans/3.2/topics/logging/
if DEBUG:
    logging_level = "DEBUG"
else:
    logging_level = "INFO"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            # "format": "%(levelname)s %(asctime)s %(module)s %(message)s",
            "format": "%(levelname)s [%(module)s] %(message)s",
        },
        "simple": {
            "format": "%(levelname)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": logging_level,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# django-ninja
NINJA_PAGINATION_PER_PAGE = 10

# DDNS Clienter
CONFIG_FILE_NAME = getenv("CONFIG_FILE_NAME", "config.toml")

CHECK_INTERVALS = getenv("CHECK_INTERVALS", 5)  # minutes
FORCE_UPDATE_INTERVALS = getenv("FORCE_UPDATE_INTERVALS", 1440)  # minutes, 1day

DISABLE_CRON = getenv("DISABLE_CRON", False)  # for dev

#
# Sentry
#
SENTRY_DSN = getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    # from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

    from ddns_clienter import __version__
    from ddns_clienter_core.runtimes.sentry import init_sentry

    init_sentry(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), LoggingIntegration()],
        app_name="PelicanPublisher",
        app_version=__version__,
        user_id_is_mac_address=True,
    )
