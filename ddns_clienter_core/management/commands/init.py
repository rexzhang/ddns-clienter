from logging import getLogger

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core import management

from crontab import CronTab

from ddns_clienter_core.runtimes.event import send_event

logger = getLogger(__name__)


def init_crontab():
    if settings.DEBUG:
        logger.info("crontab write passed!")
        return

    cron = CronTab(user="root")
    job = cron.new(
        # command="django-admin check_and_push --config /data/config.toml --send-event"
        command="wget http://127.0.0.1/api/check_and_push -o /dev/null"
    )
    job.minute.every(settings.CHECK_INTERVALS)
    cron.write()
    send_event("crontab created.")


def init_db():
    management.call_command("migrate", interactive=False)
    send_event("database init finished.")


class Command(BaseCommand):
    help = "Init DDDNS Clienter database and crontab"

    def handle(self, *args, **options):
        init_db()
        init_crontab()
