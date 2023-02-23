"""
https://gist.github.com/rexzhang/74936b88e43b928149af4237d70c3fde
"""

from typing import Any, Optional

import sentry_sdk
from sentry_sdk import configure_scope
from sentry_sdk.integrations import Integration

EVENT_RATE_LIMIT_TIME_RANGE = 60 * 60  # one hour
EVENT_RATE_LIMIT_TIMES = 10  # 10 times

Event = Optional[dict[str, Any]]
EventCounter = dict[str, list[int]]  # { key: [timestamp, count] }
event_counter: EventCounter = dict()


class StartupReport(Exception):
    pass


def auto_drop_event_for_rate_limit(event: Event, _) -> Event:
    try:
        values = event["exception"]["values"][0]
        if not isinstance(values, dict):
            raise ValueError

        key = "{}:{}:{}".format(
            values.get("module", "m"),
            values.get("type", "t"),
            values.get("value", "v"),
        )
    except ValueError:
        key = "m:t:v"

    # timestamp = int(datetime.utcnow().timestamp())
    timestamp = 0  # TODO unimplemented; check, take from event.get(timestamp)

    if key not in event_counter:
        # first event
        event_counter[key] = list((timestamp, 1))
        return event

    # count
    event_counter[key][1] += 1

    if event_counter[key][1] > EVENT_RATE_LIMIT_TIMES:
        # rate limit out, skip event
        return None

    if event_counter[key][1] == EVENT_RATE_LIMIT_TIMES:
        # last time
        with configure_scope() as scope:
            scope.set_tag(
                "rate_limit",
                f"{EVENT_RATE_LIMIT_TIMES}@{EVENT_RATE_LIMIT_TIME_RANGE}",
            )
        return event

    return event


def get_mac_address() -> str:
    from uuid import getnode

    mac = ":".join(
        [f"{(getnode() >> ele) & 0xFF:02x}" for ele in range(0, 8 * 6, 8)][::-1]
    ).upper()
    return mac


def init_sentry(
    dsn: str,
    integrations: list[Integration],
    app_name: str = "PyApp",
    app_version: str = "0.0.0",
    debug: bool = False,
    auto_rate_limit: bool = True,
    announce_at_startup: bool = True,
    user_id_is_mac_address: bool = False,
):
    if debug:
        environment = "debug"
        traces_sample_rate = 1.0
    else:
        environment = "release"
        traces_sample_rate = 0.0
        auto_rate_limit = True
        announce_at_startup = True

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=f"{app_name}@{app_version}",
        integrations=integrations,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,
        traces_sample_rate=traces_sample_rate,
        # rate limit
        before_send=auto_drop_event_for_rate_limit if auto_rate_limit else None,
    )

    mac_address = get_mac_address()
    if user_id_is_mac_address:
        with configure_scope() as scope:
            scope.set_user({"id": mac_address})

    if announce_at_startup:
        sentry_sdk.capture_exception(
            StartupReport(f"{app_name} v{app_version}@{mac_address} is up.")
        )
