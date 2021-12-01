from django.core.management.commands.migrate import Command
from django.conf import settings
from crontab import CronTab


def init_db():
    command = Command()
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


def init_crontab():
    cron = CronTab(user="root", tabfile="ddns_clienter")
    job = cron.new(command="python -m ddns_clienter check_and_push")
    job.minute.every(settings.CHECK_INTERVALS)
    cron.write()
