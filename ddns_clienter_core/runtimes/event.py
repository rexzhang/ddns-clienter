from logging import getLogger

from ddns_clienter_core.constants import EventLevel
from ddns_clienter_core.models import Event as EventModel

logger = getLogger(__name__)

__all__ = ["event"]


class AsyncEvent:
    @staticmethod
    async def _save_event(message: str, level: EventLevel):
        event_db = EventModel(level=level, message=message)
        await event_db.asave()

    async def debug(self, message: str):
        await self._save_event(message, EventLevel.INFO)

    async def info(self, message: str):
        await self._save_event(message, EventLevel.INFO)

    async def warning(self, message: str):
        await self._save_event(message, EventLevel.WARNING)

    async def error(self, message: str):
        await self._save_event(message, EventLevel.ERROR)


event = AsyncEvent()
