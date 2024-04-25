from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic import TemplateView

from ddns_clienter_core.apps import get_g
from ddns_clienter_core.runtimes.config import ConfigException, get_config
from ddns_clienter_core.runtimes.crontab import get_crontab_next_time
from ddns_clienter_core.runtimes.helpers import get_dns_servers, get_g_data
from ddns_clienter_core.runtimes.persistent_data import (
    get_addresses_values,
    get_events_queryset,
    get_tasks_queryset,
)


def convert_none_to_symbol(data: dict) -> dict:
    for key in list(data.keys()):
        if "time" in key:
            continue

        if data[key] is None or data[key] == "":
            data[key] = "-"

    return data


class DCTemplateView(TemplateView):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if context is None:
            return redirect("trouble_shooting")

        context.update({"g": get_g_data()})
        return self.render_to_response(context)


def _get_events_page(page_number: int):
    paginator = Paginator(get_events_queryset(settings.DEBUG).all(), 10)
    page_obj = paginator.get_page(page_number)
    return page_obj


class HomeView(DCTemplateView):
    template_name = "home_main.html"

    def get_context_data(self, **kwargs):
        try:
            app_config = get_config()
        except ConfigException as e:
            messages.add_message(self.request, messages.ERROR, str(e))
            return None

        kwargs = super().get_context_data(**kwargs)

        addresses = list()
        for data in get_addresses_values(settings.DEBUG).values():
            data = convert_none_to_symbol(data)
            addresses.append(data)

        tasks = list()
        for data in get_tasks_queryset(settings.DEBUG).values():
            data = convert_none_to_symbol(data)
            tasks.append(data)

        events_page = _get_events_page(1)

        next_addresses_check_time = get_crontab_next_time(
            app_config.common.check_intervals
        )
        next_task_force_update_time = get_crontab_next_time(
            app_config.common.force_update_intervals
        )
        kwargs.update(
            {
                "app_config": app_config,
                "next_addresses_check_time": next_addresses_check_time,
                "next_task_force_update_time": next_task_force_update_time,
                "addresses": addresses,
                "tasks": tasks,
                "events_page": events_page,
            }
        )
        return kwargs


class TroubleShootingView(DCTemplateView):
    template_name = "trouble_shooting.html"

    def get_context_data(self, **kwargs):
        kwargs.update(
            {
                "status": {
                    "time_zone": timezone.get_current_timezone_name(),
                    "dns": f"{', '.join(get_dns_servers())}",
                },
                "env": get_g().get("env"),
            }
        )

        return kwargs


async def add_more_event(request):
    from django.shortcuts import HttpResponse
    from django.utils.timezone import now

    from ddns_clienter_core.runtimes.event import event

    await event.info(str(now()))

    return HttpResponse()


def home_events_page(request):
    """
    Fetch paginated events and render them.
    """
    page_number = request.GET.get("page", 1)
    events_page = _get_events_page(page_number)
    return render(request, "home_event_page.html", {"events_page": events_page})
