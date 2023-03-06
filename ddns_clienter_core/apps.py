from asgiref.sync import async_to_sync
from django.apps import AppConfig


class DdnsClienterCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ddns_clienter_core"

    def ready(self):
        from ddns_clienter_core.runtimes.check_and_update import check_and_update

        print("run tasks at startup")
        async_to_sync(check_and_update)()
