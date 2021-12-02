from logging import getLogger

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands.migrate import Command as MigrateCommand
from crontab import CronTab

from ddns_clienter_core.runtimes.event import send_event

logger = getLogger(__name__)


def init_crontab():
    if settings.DEBUG:
        logger.info("crontab write passed!")
        return

    cron = CronTab(user="root")
    job = cron.new(
        command="python -m ddns_clienter check_and_push --config /data/config.toml"
    )
    job.minute.every(settings.CHECK_INTERVALS)
    cron.write()
    send_event("crontab created.")


def init_db():
    command = MigrateCommand()
    migrate_options = {
        # BaseCommand
        "verbosity": 0,
        # Command in migrate
        "skip_checks": None,
        "interactive": False,
        "database": "default",
        "run_syncdb": None,
        "app_label": None,
        "check_unapplied": None,
        "plan": None,
        "fake": None,
        "fake_initial": None,
    }
    command.handle(**migrate_options)
    send_event("database init finished.")


class Command(BaseCommand):
    help = "Check the IP Address and push it to DDNS provider if there is a change"

    def handle(self, *args, **options):
        init_db()
        init_crontab()
