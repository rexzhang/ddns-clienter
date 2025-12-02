from logging import getLogger

from django.core.management.base import BaseCommand

from ddns_clienter.core.runtimes.crontab import update_crontab_file
from ddns_clienter.ev import EV

logger = getLogger(__name__)


def init_crontab():
    if EV.DISABLE_CRON:
        logger.info("Init: crontab update skipped!")
        return

    update_crontab_file()


class Command(BaseCommand):
    help = "Init DDDNS Clienter database and crontab"

    def handle(self, *args, **options):
        init_crontab()
