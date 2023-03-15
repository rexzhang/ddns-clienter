from logging import getLogger

from asgiref.sync import sync_to_async

from ddns_clienter_core.constants import EventLevel
from ddns_clienter_core.models import Event as EventModel

logger = getLogger(__name__)

__all__ = ["event"]


class AsyncEvent:
    @staticmethod
    async def _save_event(message: str, level: EventLevel):
        event_db = EventModel(level=level, message=message)
        await sync_to_async(event_db.save)()

    async def debug(self, message: str):
        await self._save_event(message, EventLevel.INFO)

    async def info(self, message: str):
        await self._save_event(message, EventLevel.INFO)

    async def warning(self, message: str):
        await self._save_event(message, EventLevel.WARNING)

    async def error(self, message: str):
        await self._save_event(message, EventLevel.ERROR)


event = AsyncEvent()


async def send_event(message: str, level: EventLevel = EventLevel.INFO):
    event_db = EventModel(level=level, message=message)
    await sync_to_async(event_db.save)()
