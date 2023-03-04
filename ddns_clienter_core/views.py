from django.views.generic import TemplateView

from ddns_clienter import __name__ as name
from ddns_clienter import __project_url__, __version__
from ddns_clienter_core.runtimes.config import get_config
from ddns_clienter_core.runtimes.persistent_data import (
    get_addresses_values,
    get_events_values,
    get_tasks_queryset,
)


def convert_none_to_symbol(data: dict) -> dict:
    for key in list(data.keys()):
        if "time" in key:
            continue

        if data[key] is None or data[key] == "":
            data[key] = "-"

    return data


class IndexView(TemplateView):
    template_name = "index_v2.html"

    def get_context_data(self, **kwargs):
        config = get_config()
        kwargs = super().get_context_data(**kwargs)

        addresses = list()
        for data in get_addresses_values(config).values():
            data = convert_none_to_symbol(data)

            addresses.append(data)

        tasks = list()
        for data in get_tasks_queryset(config).values():
            data = convert_none_to_symbol(data)

            if data["host"] == "-":
                data["full_domain"] = data["domain"]
            else:
                data["full_domain"] = "{}.{}".format(data["host"], data["domain"])

            tasks.append(data)

        events = list()
        for data in get_events_values(config):
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
                "app_config": config,
                "addresses": addresses,
                "tasks": tasks,
                "events": events,
            }
        )
        return kwargs
