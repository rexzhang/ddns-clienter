from datetime import timedelta
from django.conf import settings
from django.utils import timezone

from ddns_clienter_core.models import Address, Task, Event


def get_addresses(full: bool = False):
    if full:
        queryset = Address.objects
    else:
        queryset = Address.objects.filter(
            time__gt=(timezone.now() - timedelta(minutes=settings.CHECK_INTERVALS * 2))
        )

    addresses = queryset.order_by("name").all()
    return addresses


def get_tasks(full: bool = False):
    if full:
        queryset = Task.objects
    else:
        queryset = Task.objects.filter(
            time__gt=(
                timezone.now() - timedelta(minutes=settings.FORCE_UPDATE_INTERVALS * 2)
            )
        )

    tasks = queryset.order_by("name").all()
    return tasks


def get_events(full: bool = False):
    if full:
        events = Event.objects.order_by("-time").all()
    else:
        events = Event.objects.order_by("-time")[:10]

    return events
