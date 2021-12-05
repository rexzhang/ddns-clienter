from logging import getLogger

from django.db import models

from ddns_clienter_core.models import Event

logger = getLogger(__name__)

__all__ = ["EventLevel", "send_event"]


class EventLevel(models.TextChoices):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def send_event(message: str, level: EventLevel = EventLevel.INFO):
    event = Event(level=level, message=message)
    event.save()
    logger.info("{} {}".format(level, message))
