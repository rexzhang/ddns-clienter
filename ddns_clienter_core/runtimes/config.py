from dataclasses import dataclass, field
from logging import getLogger

import toml

from ddns_clienter_core.models import EventLevel
from ddns_clienter_core.runtimes.event import send_event

logger = getLogger(__name__)


@dataclass
class ConfigAddress:
    name: str

    ipv4: bool = False
    ipv6: bool = False
    ipv4_match_rule: str = ""
    ipv6_match_rule: str = ""

    provider: str = field(default=None)  # ip address detect provider's name
    parameter: str = ""  # for ip address detect provider


@dataclass
class ConfigTask:
    name: str

    address_name: str
    ipv4: bool = False
    ipv6: bool = False

    domain: str = field(default=None)
    host: str = field(default=None)

    provider: str = field(default=None)
    provider_token: str = field(default=None)


class ConfigException(Exception):
    pass


class Config:
    addresses = dict()
    tasks = list()

    def __init__(self, file_name: str):
        self._file_name = file_name
        self.load_from_file()

    def load_from_file(self):
        try:
            obj = toml.load(self._file_name)
        except FileNotFoundError as e:
            logger.error(e)
            send_event(
                "Can not open config file:{}".format(self._file_name),
                level=EventLevel.CRITICAL,
            )
            raise ConfigException(e)

        addresses_obj: dict = obj.get("addresses")
        tasks_obj: dict = obj.get("tasks")
        if addresses_obj is None or tasks_obj is None:
            raise

        for name, data in addresses_obj.items():
            address_info = ConfigAddress(name=name, **data)
            if not address_info.ipv4 and not address_info.ipv6:
                raise Exception("ipv4 ipv6 both disable")

            self.addresses.update({name: address_info})

        for name, data in tasks_obj.items():
            task = ConfigTask(name=name, **data)
            if not task.ipv4 and not task.ipv6:
                raise Exception("ipv4 ipv6 both disable")

            self.tasks.append(task)

        # TODO: check
