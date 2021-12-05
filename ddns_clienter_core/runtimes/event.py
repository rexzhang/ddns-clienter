from logging import getLogger

from ddns_clienter_core.constants import EventLevel
from ddns_clienter_core.models import Event

logger = getLogger(__name__)

__all__ = ["send_event"]


def send_event(message: str, level: EventLevel = EventLevel.INFO):
    event = Event(level=level, message=message)
    event.save()
    logger.info("{} {}".format(level, message))
