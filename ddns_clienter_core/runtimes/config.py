from dataclasses import dataclass, field
from logging import getLogger

import toml

logger = getLogger(__name__)


@dataclass
class Common:
    check_intervals: int = field(default=5)  # minutes
    force_update_intervals: int = field(default=1440)  # minutes, 1day


@dataclass
class AddressConfig:
    name: str

    ipv4: bool = False
    ipv6: bool = False
    ipv6_prefix_length: int | None = None
    ipv4_match_rule: str = ""
    ipv6_match_rule: str = ""

    provider: str = field(default=None)  # ip address detect provider's name
    parameter: str = ""  # for ip address detect provider


@dataclass
class TaskConfig:
    name: str

    address_name: str
    ipv4: bool = False
    ipv6: bool = False

    provider: str = field(default=None)
    provider_token: str = field(default=None)

    domain: str = field(default=None)
    host: str = field(default=None)


class ConfigException(Exception):
    pass


class Config:
    common: Common
    addresses: list[AddressConfig]
    tasks: list[TaskConfig]

    def __init__(self, file_name: str):
        self.addresses = list()  #
        self.tasks = list()

        self._file_name = file_name
        self.load_from_file()

    def load_from_file(self):
        try:
            obj = toml.load(self._file_name)
        except FileNotFoundError as e:
            logger.error(e)
            logger.error("Can not open config file:{}".format(self._file_name))
            raise ConfigException(e)

        # common
        common_obj = obj.get("common")
        if common_obj is None:
            self.common = Common()
        else:
            self.common = Common(obj.get("common"))

        # addresses
        addresses_obj: dict = obj.get("addresses")
        tasks_obj: dict = obj.get("tasks")
        if addresses_obj is None or tasks_obj is None:
            raise

        for name, data in addresses_obj.items():
            address_info = AddressConfig(name=name, **data)
            if not address_info.ipv4 and not address_info.ipv6:
                raise Exception("ipv4 ipv6 both disable")

            self.addresses.append(address_info)

        # tasks
        for name, data in tasks_obj.items():
            task = TaskConfig(name=name, **data)
            if not task.ipv4 and not task.ipv6:
                raise Exception("ipv4 ipv6 both disable")

            self.tasks.append(task)

        # TODO: check
