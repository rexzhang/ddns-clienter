from django.apps import AppConfig

import ddns_clienter
from ddns_clienter_core.runtimes.helpers import get_dns_servers

running_contents: dict | None = None


def _init_running_contents():
    global running_contents

    web_ui_footer = {"DNS": f"{','.join(get_dns_servers())}"}
    running_contents = {
        "app_name": ddns_clienter.__name__,
        "app_version": ddns_clienter.__version__,
        "app_url": ddns_clienter.__project_url__,
        "web_ui_footer": web_ui_footer,
    }


class DdnsClienterCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ddns_clienter_core"

    def ready(self):
        _init_running_contents()
