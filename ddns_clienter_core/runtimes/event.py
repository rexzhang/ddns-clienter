from logging import getLogger

from asgiref.sync import sync_to_async

from ddns_clienter_core.constants import EventLevel
from ddns_clienter_core.models import Event

logger = getLogger(__name__)

__all__ = ["send_event"]


async def send_event(message: str, level: EventLevel = EventLevel.INFO):
    event = Event(level=level, message=message)
    await sync_to_async(event.save)()
