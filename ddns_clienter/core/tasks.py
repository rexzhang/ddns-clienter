import asyncio

from django.tasks import task

from ddns_clienter.core.runtimes.check_and_update import _check_an_update_v2
from ddns_clienter.core.runtimes.helpers import (
    send_sse_event,
    send_sse_event_reload,
)

_check_and_update_running_lock = asyncio.Lock()


@task
async def test_task() -> str:
    await asyncio.sleep(1)
    return "TEST is OK"


@task
async def check_and_update() -> str:
    if _check_and_update_running_lock.locked():
        return "There are already tasks in progress, please try later"

    send_sse_event("status:check_update", "Check/Update is running")
    async with _check_and_update_running_lock:
        await asyncio.sleep(3)
        await _check_an_update_v2()

    send_sse_event("status:check_update", "")
    send_sse_event_reload()
    return ""
