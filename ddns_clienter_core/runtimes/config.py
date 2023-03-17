import tomllib
from dataclasses import dataclass, field
from logging import getLogger

from django.conf import settings

from ddns_clienter_core.constants import CHECK_INTERVALS

logger = getLogger(__name__)


@dataclass
class Common:
    check_intervals: int = field(default=CHECK_INTERVALS)  # minutes
    force_update_intervals: int = field(default=1440)  # minutes, 1day


@dataclass
class AddressProviderConfig:
    name: str

    provider_name: str

    # have default value ---
    enable: bool = True

    provider_parameter: str = ""

    ipv4: bool = False
    ipv6: bool = False
    ipv6_prefix_length: int | None = None
    ipv4_match_rule: str = ""
    ipv6_match_rule: str = ""
    allow_private: bool = False
    allow_loopback: bool = False

    def __post_init__(self):
        if self.allow_loopback:
            self.allow_private = True


@dataclass
class TaskConfig:
    name: str

    provider_name: str
    provider_auth: str

    address_name: str

    domain: str

    # have default value ---
    enable: bool = True

    ipv4: bool = False
    ipv6: bool = False


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
        except (OSError, tomllib.TOMLDecodeError) as e:
            message = f"Open config file file:{self._file_name} failed; {e}"
            raise ConfigException(message)

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
                message = f"Parser Config file failed, [addresses.{name}]; {e}"
                raise ConfigException(message)

            if not address_provider_config.ipv4 and not address_provider_config.ipv6:
                message = f"Parser Config file failed, [addresses.{name}]; ipv4 ipv6 both disable"
                raise ConfigException(message)

            self.addresses.update({name: address_provider_config})

        # tasks
        for name, data in tasks_obj.items():
            host = data.pop("host", None)
            if host is not None and len(host) >= 1:
                message = f"task.host is deprecated"  # TODO

                domain = data.get("domain", "")
                data["domain"] = f"{host}.{domain}"

            try:
                task = TaskConfig(name=name, **data)
            except TypeError as e:
                message = f"Parser Config file failed, [tasks.{name}]; {e}"
                raise ConfigException(message)

            if not task.ipv4 and not task.ipv6:
                message = (
                    f"Parser Config file failed, [tasks.{name}]; ipv4 ipv6 both disable"
                )
                raise ConfigException(message)

            self.tasks.update({name: task})


def get_config(config_file_name: str = None) -> Config:
    if config_file_name is None:
        config_file_name = settings.CONFIG_FILE

    config = Config(config_file_name)

    return config
