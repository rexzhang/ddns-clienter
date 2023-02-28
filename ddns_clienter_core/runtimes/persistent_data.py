from datetime import timedelta

from django.utils import timezone

from ddns_clienter_core.models import Address, Event, Task
from ddns_clienter_core.runtimes.config import Config


def get_addresses_values(config: Config, debug: bool = False):
    if debug:
        queryset = Address.objects
    else:
        queryset = Address.objects.filter(name__in=config.addresses.keys())

    return queryset.order_by("name").all().values()


def get_tasks_values(config: Config, debug: bool = False):
    if debug:
        queryset = Task.objects
    else:
        queryset = Task.objects.filter(name__in=config.tasks.keys())

    return queryset.order_by("name").all().values()


def get_events_values(config: Config, debug: bool = False):
    if debug:
        queryset = Event.objects.all()
    else:
        queryset = Event.objects.filter(time__gt=(timezone.now() - timedelta(days=2)))

    return queryset.order_by("-id").values()
