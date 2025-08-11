from django.apps import AppConfig
from django.conf import settings

import ddns_clienter
from ddns_clienter_core.runtimes.config import env

_app_g = None


def get_g() -> dict:
    global _app_g
    if _app_g is None:
        _app_g = {
            "app": {
                "name": ddns_clienter.__name__,
                "version": ddns_clienter.__version__,
                "github_url": ddns_clienter.__project_url__,
                "docker_url": ddns_clienter.__docker_url__,
            },
            "status": {
                "debug_mode": settings.DEBUG,
            },
            "env": {
                "DATA_PATH": env.DATA_PATH,
                "CONFIG_TOML": env.CONFIG_TOML,
                "PBULIC_INSIDE_API": env.PBULIC_INSIDE_API,
            },
        }

    return _app_g


class DdnsClienterCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ddns_clienter_core"

    def ready(self):
        get_g()
