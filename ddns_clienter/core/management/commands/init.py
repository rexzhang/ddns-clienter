from logging import getLogger

from asgiref.sync import async_to_sync
from core.runtimes.crontab import update_crontab_file
from core.runtimes.event import event
from django.core import management
from django.core.management.base import BaseCommand

from ddns_clienter.ev import EV

logger = getLogger(__name__)

_CRON_COMMENT_TAG = "DDNS Clienter"


def init_crontab():
    if EV.DISABLE_CRON:
        logger.info("Init: crontab update skipped!")
        return

    update_crontab_file()


def init_db():
    management.call_command("migrate", interactive=False)
    message = "Init: database init finished."
    logger.info(message)
    async_to_sync(event.info)(message)


class Command(BaseCommand):
    help = "Init DDDNS Clienter database and crontab"

    def handle(self, *args, **options):
        init_db()
        init_crontab()
