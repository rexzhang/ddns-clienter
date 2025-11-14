from django_eventstream import send_event

from ddns_clienter.core.apps import get_g
from ddns_clienter.core.runtimes.config import ConfigException, get_config


def get_dns_servers() -> list[str]:
    dns_servers = list()
    with open("/etc/resolv.conf") as f:
        for line in f:
            if line.startswith("nameserver"):
                parts = line.split()
                if len(parts) > 1:
                    dns_servers.append(parts[1])

    return dns_servers


def get_g_data() -> dict:
    g_data = get_g()
    try:
        app_config = get_config()
    except ConfigException:
        app_config = None

    g_data["status"].update(
        {
            "config_check": False if app_config is None else True,
        }
    )

    return g_data


def send_sse_event(event: str, data: str):
    send_event("root", event, data, json_encode=False)


def send_sse_event_reload():
    send_event(
        "root",
        "reload",
        "window.location.reload();",
        json_encode=False,
    )
