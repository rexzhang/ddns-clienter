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

    url = "http://127.0.0.1:8000/api/check_and_update"
    if settings.DEBUG:
        command = "/usr/bin/wget {} -o /{}/dc-cron.log".format(
            url, settings.BASE_DATA_DIR
        )
    else:
        command = "/usr/bin/wget {} -o /dev/null".format(url)
    if settings.WORK_IN_CONTAINER:
        crontab_filename = "/etc/crontabs/root"
    else:
        crontab_filename = "/tmp/dc-crontab"

    cron = CronTab()
    cron.remove_all(comment=_CRON_COMMENT_TAG)
    job = cron.new(command=command, comment=_CRON_COMMENT_TAG)
    job.minute.every(settings.CONFIG.common.check_intervals)
    cron.write(crontab_filename)

    message = "crontab file:{} created/updated.".format(crontab_filename)
    logger.info(message)
    send_event(message)


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
