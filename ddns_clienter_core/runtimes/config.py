from dataclasses import dataclass
from logging import getLogger

import toml

from ddns_clienter_core.models import EventLevel
from ddns_clienter_core.runtimes.event import send_event

logger = getLogger(__name__)


@dataclass
class Address:
    name: str
    provider: str  # ip address detect provider's name
    parameter: str = ""  # for ip address detect provider

    ipv4: bool = False
    ipv6: bool = False
    ipv4_match_rule: str = ""
    ipv6_match_rule: str = ""


@dataclass
class Domain:
    name: str

    provider: str
    provider_token: str

    domain: str
    host: str

    address_name: str
    ipv4: bool = False
    ipv6: bool = False


class ConfigException(Exception):
    pass


class Config:
    addresses = dict()
    domains = list()

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
        tasks_obj: dict = obj.get("domains")
        if addresses_obj is None or tasks_obj is None:
            raise

        for name, data in addresses_obj.items():
            address_info = Address(name=name, **data)
            if not address_info.ipv4 and not address_info.ipv6:
                raise Exception("ipv4 ipv6 both disable")

            self.addresses.update({name: address_info})

        for name, data in tasks_obj.items():
            task = Domain(name=name, **data)
            if not task.ipv4 and not task.ipv6:
                raise Exception("ipv4 ipv6 both disable")

            self.domains.append(task)
