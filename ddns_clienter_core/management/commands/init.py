from logging import getLogger

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core import management

from crontab import CronTab

from ddns_clienter_core.runtimes.event import send_event

logger = getLogger(__name__)

_CRON_COMMENT_TAG = "DDNS Clienter"


def init_crontab():
    if settings.DISABLE_CRON:
        logger.info("crontab update skipped!")
        return

    if settings.DEBUG:
        command = "/usr/bin/wget http://127.0.0.1:8000/api/check_and_update -o /data/dc-cron.log"
    else:
        command = (
            "/usr/bin/wget http://127.0.0.1:8000/api/check_and_update -o /dev/null"
        )

    cron = CronTab()
    cron.remove_all(comment=_CRON_COMMENT_TAG)
    job = cron.new(command=command, comment=_CRON_COMMENT_TAG)
    job.minute.every(settings.CHECK_INTERVALS)
    cron.write("/etc/crontabs/root")
    send_event("crontab created/updated.")


def init_db():
    management.call_command("migrate", interactive=False)
    message = "database init finished."
    logger.info(message)
    send_event(message)


class Command(BaseCommand):
    help = "Init DDDNS Clienter database and crontab"

    def handle(self, *args, **options):
        init_db()
        init_crontab()
