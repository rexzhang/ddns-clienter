from django.shortcuts import redirect
from django.views.generic import TemplateView

from ddns_clienter import __name__ as name
from ddns_clienter import __project_url__, __version__
from ddns_clienter_core.runtimes.check_and_update import check_and_update_is_running
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


class DCException(Exception):
    pass


class DCExceptionLoadConfigFailed(DCException):
    pass


class DCTemplateView(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            context = self.get_context_data(**kwargs)
        except DCExceptionLoadConfigFailed:
            return redirect("failed_load_config")
        except DCException:
            raise

        if not isinstance(context, dict):
            raise

        context.update(
            {
                "app_name": name,
                "app_version": __version__,
                "app_url": __project_url__,
            }
        )
        return self.render_to_response(context)


class HomePageView(DCTemplateView):
    template_name = "home_page.html"

    # def get(self, request, *args, **kwargs):
    #     context = self.get_context_data(**kwargs)
    #     if context is None:
    #         return redirect("failed_load_config")
    #
    #     else:
    #         return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        app_config = get_config()
        if app_config is None:
            raise DCExceptionLoadConfigFailed

        kwargs = super().get_context_data(**kwargs)

        addresses = list()
        for data in get_addresses_values(app_config).values():
            data = convert_none_to_symbol(data)

            addresses.append(data)

        tasks = list()
        for data in get_tasks_queryset(app_config).values():
            data = convert_none_to_symbol(data)

            if data["host"] == "-":
                data["full_domain"] = data["domain"]
            else:
                data["full_domain"] = "{}.{}".format(data["host"], data["domain"])

            tasks.append(data)

        events = list()
        for data in get_events_values():
            if data["level"] in {"WARNING", "ERROR", "CRITICAL"}:
                data["highlight"] = True
            else:
                data["highlight"] = False

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


class FailedViewLoadConfig(DCTemplateView):
    template_name = "failed_load_config.html"
