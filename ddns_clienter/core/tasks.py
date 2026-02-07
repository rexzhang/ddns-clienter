import asyncio
from logging import getLogger

from django.tasks import task

from ddns_clienter.core.runtimes.check_and_update import check_an_update_v2
from ddns_clienter.core.runtimes.event import event
from ddns_clienter.core.runtimes.helpers import (
    send_sse_event,
    send_sse_event_reload,
)

logger = getLogger(__name__)

_check_and_update_running_lock = asyncio.Lock()


@task
async def test_task() -> None:
    await asyncio.sleep(1)

    await event.info("TEST is OK")
    return


@task
async def check_and_update() -> None:
    if _check_and_update_running_lock.locked():
        message = "There are already tasks in progress, please try later"
        await event.warning(message)
        logger.warning(message)
        return

    send_sse_event("status:check_update", "Check/Update is running")
    async with _check_and_update_running_lock:
        await asyncio.sleep(0)
        await check_an_update_v2()

    send_sse_event("status:check_update", "")
    send_sse_event_reload()

    message = "Check/Update is done"
    await event.warning(message)
    logger.warning(message)
    return
