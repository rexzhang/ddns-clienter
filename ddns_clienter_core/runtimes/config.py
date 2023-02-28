import tomllib
from dataclasses import dataclass, field
from logging import getLogger

from django.conf import settings

logger = getLogger(__name__)


@dataclass
class Common:
    check_intervals: int = field(default=5)  # minutes
    force_update_intervals: int = field(default=1440)  # minutes, 1day


@dataclass
class AddressProviderConfig:
    name: str

    ipv4: bool = False
    ipv6: bool = False
    ipv6_prefix_length: int | None = None
    ipv4_match_rule: str = ""
    ipv6_match_rule: str = ""
    allow_private: bool = False
    allow_loopback: bool = False

    provider_name: str = field(default=None)  # ip address provider's name
    provider_parameter: str = ""  # ip address provider's parameter

    def __post_init__(self):
        if self.allow_loopback:
            self.allow_private = True


@dataclass
class TaskConfig:
    name: str

    address_name: str
    ipv4: bool = False
    ipv6: bool = False

    provider: str = field(default=None)
    provider_auth: str = field(default=None)

    domain: str = field(default=None)
    host: str = field(default=None)


class ConfigException(Exception):
    pass


class Config:
    common: Common
    addresses: dict[str, AddressProviderConfig]
    tasks: dict[str, TaskConfig]

    def __init__(self, file_name: str):
        self.addresses = dict()
        self.tasks = dict()

        self._file_name = file_name
        self.load_from_file()

    def load_from_file(self):
        try:
            with open(self._file_name, "rb") as f:
                obj = tomllib.load(f)
        except (FileNotFoundError, tomllib.TOMLDecodeError) as e:
            logger.error(e)
            logger.error(f"Can not open config file:{self._file_name}")
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
            try:
                address_provider_config = AddressProviderConfig(name=name, **data)
            except TypeError as e:
                raise Exception(f"Parser Config file failed, [addresses.{name}], {e}")

            if not address_provider_config.ipv4 and not address_provider_config.ipv6:
                raise Exception("ipv4 ipv6 both disable")

            self.addresses.update({name: address_provider_config})

        # tasks
        for name, data in tasks_obj.items():
            task = TaskConfig(name=name, **data)
            if not task.ipv4 and not task.ipv6:
                raise Exception("ipv4 ipv6 both disable")

            self.tasks.update({name: task})

        # TODO: check


def get_config(config_file_name: str = None):
    if config_file_name is None:
        config_file_name = settings.CONFIG_FILE

    return Config(config_file_name)
