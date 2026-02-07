from datetime import timedelta
from logging import getLogger

from asgiref.sync import async_to_sync
from crontab import CronTab
from django.conf import settings

from ddns_clienter.core.runtimes.event import event
from ddns_clienter.ev import EV

logger = getLogger(__name__)

_INSIDE_API_URL = "http://127.0.0.1:8000/api/check_and_update"
_CRON_COMMENT_TAG = "DDNS Clienter"


def get_crontab_next_time(intervals: int):
    cron = CronTab(tab="")
    job = cron.new()
    job.minute.every(5)
    return job.schedule().get_next() + timedelta(minutes=intervals - 5)


def update_crontab_file():
    if EV.DEPLOY_IN_CONTAINER:
        filename = "/etc/crontabs/root"
    else:
        filename = "/tmp/ddns-clienter-crontabs"

    if settings.DEBUG:
        command = f"/usr/bin/wget {_INSIDE_API_URL} -o /tmp/dc-cron.log"
    else:
        command = f"/usr/bin/wget {_INSIDE_API_URL} -o /dev/null"

    cron = CronTab()
    cron.remove_all(comment=_CRON_COMMENT_TAG)
    job = cron.new(command=command, comment=_CRON_COMMENT_TAG)

    job.minute.every(5)
    cron.write(filename)

    message = f"Init: crontab file:{filename} created/updated."
    logger.info(message)
    async_to_sync(event.info)(message)
