from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView

from ddns_clienter_core.apps import running_contents
from ddns_clienter_core.runtimes.check_and_update import check_and_update_is_running
from ddns_clienter_core.runtimes.config import ConfigException, get_config
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

        context.update(running_contents)
        return self.render_to_response(context)


class HomePageView(DCTemplateView):
    template_name = "home_page.html"

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

        events = list()
        for data in get_events_queryset(settings.DEBUG).values():
            events.append(data)

        kwargs.update(
            {
                "app_config": app_config,
                "check_and_update_is_running": check_and_update_is_running(),
                "addresses": addresses,
                "tasks": tasks,
                "events": events,
            }
        )
        return kwargs


class TroubleShootingView(DCTemplateView):
    template_name = "trouble_shooting.html"
