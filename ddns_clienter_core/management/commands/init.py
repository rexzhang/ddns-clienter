from logging import getLogger

from asgiref.sync import async_to_sync
from crontab import CronTab
from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand

from ddns_clienter_core.runtimes.crontab import update_crontab_file
from ddns_clienter_core.runtimes.event import send_event

logger = getLogger(__name__)

_CRON_COMMENT_TAG = "DDNS Clienter"


def init_crontab():
    if settings.DISABLE_CRON:
        logger.info("crontab update skipped!")
        return

    update_crontab_file()


def init_db():
    management.call_command("migrate", interactive=False)
    message = "database init finished."
    logger.info(message)
    async_to_sync(send_event)(message)


class Command(BaseCommand):
    help = "Init DDDNS Clienter database and crontab"

    def handle(self, *args, **options):
        init_db()
        init_crontab()
