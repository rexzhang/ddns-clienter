from django.shortcuts import render
from django.conf import settings
from django.views.generic import TemplateView

from ddns_clienter import __name__ as name, __version__, __project_url__
from ddns_clienter_core.runtimes.persistent_data import (
    get_addresses_values,
    get_tasks_values,
    get_events_values,
)


def index_view(request):
    context = {
        "name": name,
        "version": __version__,
        "project_url": __project_url__,
    }
    return render(request, "index.html", context)


def convert_none_to_symbol(data: dict) -> dict:
    for key in data.keys():
        if "time" in key:
            continue

        if data[key] is None or data[key] == "":
            data[key] = "-"

    return data


class IndexView(TemplateView):
    template_name = "index_v2.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        if settings.DEBUG:
            full = True
        else:
            full = False

        addresses = list()
        for data in get_addresses_values(full):
            data = convert_none_to_symbol(data)

            addresses.append(data)

        tasks = list()
        for data in get_tasks_values(full):
            if data["host"] is None or data["host"] == "":
                data["full_domain"] = data["domain"]
            else:
                data["full_domain"] = "{}.{}".format(data["host"], data["domain"])

            # data = convert_none_to_symbol(data)

            tasks.append(data)

        events = list()
        for data in get_events_values(full):
            if data["level"] in {"WARNING", "ERROR", "CRITICAL"}:
                data["highlight"] = True
            else:
                data["highlight"] = False

            events.append(data)

        kwargs.update(
            {
                "app_name": name,
                "app_version": __version__,
                "app_url": __project_url__,
                "app_config": settings.CONFIG,
                "addresses": addresses,
                "tasks": tasks,
                "events": events,
            }
        )
        return kwargs
