import tomllib
from functools import cached_property
from logging import getLogger

import pydantic
from django.conf import settings

from ddns_clienter_core.constants import CHECK_INTERVALS

logger = getLogger(__name__)


class Common(pydantic.BaseModel):
    check_intervals: int = CHECK_INTERVALS  # minutes
    force_update_intervals: int = 1440  # minutes, 1day


class AddressProviderConfig(pydantic.BaseModel):
    name: str
    enable: bool = True

    provider_name: str
    provider_parameter: str = ""

    ipv4: bool = False
    ipv4_match_rule: str = ""
    ipv6: bool = False
    ipv6_prefix_length: int | None = None
    ipv6_match_rule: str = ""
    allow_private: bool = False
    allow_loopback: bool = False

    def model_post_init(self, _):
        if self.allow_loopback:
            self.allow_private = True


class TaskConfig(pydantic.BaseModel):
    name: str
    enable: bool = True

    address_name: str
    ipv4: bool = False
    ipv6: bool = False

    domain: str
    provider_name: str
    provider_auth: str


class ConfigException(Exception):
    pass


class Config(pydantic.BaseModel):
    common: Common = Common()

    address: list[AddressProviderConfig]
    task: list[TaskConfig]

    @cached_property
    def address_dict(self) -> dict[str, AddressProviderConfig]:
        address_dict = dict()
        for address_config in self.address:
            address_dict[address_config.name] = address_config

        return address_dict

    @cached_property
    def task_dict(self) -> dict[str, TaskConfig]:
        task_dict = dict()
        for task_config in self.task:
            task_dict[task_config.name] = task_config

        return task_dict


def get_config(config_toml: str | None = None) -> Config:
    if config_toml is None:
        config_toml = settings.CONFIG_TOML

    logger.info(f"Config: Open file {config_toml}...")
    try:
        with open(config_toml, "rb") as f:
            config_obj = tomllib.load(f)

    except FileNotFoundError as e:
        message = f"Config: Open file {config_toml} failed, {e}"
        logger.critical(message)
        raise ConfigException(message)

    except tomllib.TOMLDecodeError as e:
        message = f"Config: Parse file {config_toml} failed, {e}"
        logger.critical(message)
        raise ConfigException(message)

    try:
        config = Config.model_validate(config_obj)

    except pydantic.ValidationError as e:
        message = f"Config: Parse file {config_toml} failed, {e.errors()}"
        logger.critical(message)
        raise ConfigException(message)

    return config
