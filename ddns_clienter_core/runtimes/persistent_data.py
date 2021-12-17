from datetime import timedelta
from django.conf import settings
from django.utils import timezone

from ddns_clienter_core.models import Address, Task, Event


def get_addresses_values(full: bool = False):
    if full:
        queryset = Address.objects
    else:
        queryset = Address.objects.filter(
            time__gt=(timezone.now() - timedelta(minutes=settings.CHECK_INTERVALS * 2))
        )

    return queryset.order_by("name").all().values()


def get_tasks_values(full: bool = False):
    if full:
        queryset = Task.objects
    else:
        queryset = Task.objects.filter(
            time__gt=(
                timezone.now() - timedelta(minutes=settings.FORCE_UPDATE_INTERVALS * 2)
            )
        )

    return queryset.order_by("name").all().values()


def get_events_values(full: bool = False):
    queryset = Event.objects.order_by("-id")
    if full:
        queryset = queryset.all()
    else:
        queryset = queryset.all()[:10]

    return queryset.values()
