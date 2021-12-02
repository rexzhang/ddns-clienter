from logging import getLogger

from ddns_clienter_core.models import Event, EventLevel

logger = getLogger(__name__)


def send_event(message: str, level: EventLevel = EventLevel.INFO):
    event = Event(level=level, message=message)
    event.save()
    logger.info("{} {}".format(level, message))
