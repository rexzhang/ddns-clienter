from logging import getLogger

from asgiref.sync import async_to_sync
from crontab import CronTab
from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand

from ddns_clienter_core.runtimes.config import get_config
from ddns_clienter_core.runtimes.event import send_event

logger = getLogger(__name__)

_CRON_COMMENT_TAG = "DDNS Clienter"


def init_crontab():
    if settings.DISABLE_CRON:
        logger.info("crontab update skipped!")
        return

    url = "http://127.0.0.1:8000/api/check_and_update"
    if settings.DEBUG:
        command = f"/usr/bin/wget {url} -o /{settings.DATA_PATH}/dc-cron.log"
    else:
        command = f"/usr/bin/wget {url} -o /dev/null"
    if settings.WORK_IN_CONTAINER:
        crontab_filename = "/etc/crontabs/root"
    else:
        crontab_filename = "/tmp/dc-crontab"

    cron = CronTab()
    cron.remove_all(comment=_CRON_COMMENT_TAG)
    job = cron.new(command=command, comment=_CRON_COMMENT_TAG)
    job.minute.every(get_config().common.check_intervals)
    cron.write(crontab_filename)

    message = f"crontab file:{crontab_filename} created/updated."
    logger.info(message)
    async_to_sync(send_event)(message)


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
