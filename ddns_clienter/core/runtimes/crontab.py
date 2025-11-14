from logging import getLogger

from asgiref.sync import async_to_sync
from crontab import CronTab
from django.conf import settings

from ddns_clienter.core.constants import CHECK_INTERVALS
from ddns_clienter.core.runtimes.config import ConfigException, env, get_config
from ddns_clienter.core.runtimes.event import event

logger = getLogger(__name__)

_INSIDE_API_URL = "http://127.0.0.1:8000/api/check_and_update"
_CRON_COMMENT_TAG = "DDNS Clienter"


def get_crontab_next_time(intervals: int):
    cron = CronTab(tab="")
    job = cron.new()
    job.minute.every(intervals)
    return job.schedule().get_next()


def update_crontab_file():
    if env.WORK_IN_CONTAINER:
        filename = "/etc/crontabs/root"
    else:
        filename = "/tmp/dc-crontab"

    if settings.DEBUG:
        command = f"/usr/bin/wget {_INSIDE_API_URL} -o /{env.DATA_PATH}/dc-cron.log"
    else:
        command = f"/usr/bin/wget {_INSIDE_API_URL} -o /dev/null"

    cron = CronTab()
    cron.remove_all(comment=_CRON_COMMENT_TAG)
    job = cron.new(command=command, comment=_CRON_COMMENT_TAG)

    try:
        config = get_config()
        job.minute.every(config.common.check_intervals)
    except ConfigException as e:
        job.minute.every(CHECK_INTERVALS)
        logger.critical(e)

    cron.write(filename)

    message = f"Init: crontab file:{filename} created/updated."
    logger.info(message)
    async_to_sync(event.info)(message)
