import tomllib
from dataclasses import dataclass, field
from functools import cached_property
from logging import getLogger

from cachetools.func import ttl_cache
from dataclass_wizard import EnvWizard, JSONWizard

from ddns_clienter_core.constants import CHECK_INTERVALS

logger = getLogger(__name__)

UNDEFINED = "undefined"


class ConfigException(Exception):
    pass


class Env(EnvWizard):
    class _(EnvWizard.Meta):
        env_file = True

    # django
    DEBUG: bool = False
    TZ: str = "UTC"

    # dev
    SENTRY_DSN: str = ""

    # project base
    CONFIG_TOML: str = "ddns-clienter.toml"
    DATA_PATH: str = "."

    # project extra
    PBULIC_INSIDE_API: bool = True
    WORK_IN_CONTAINER: bool = False
    DISABLE_CRON: bool = False


env = Env()


@dataclass
class Common:
    check_intervals: int = CHECK_INTERVALS  # minutes
    force_update_intervals: int = 1440  # minutes, 1day

    sentry_dsn: str = ""


@dataclass
class AddressProviderConfig:
    name: str
    enable: bool = True

    provider_name: str = UNDEFINED
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


@dataclass
class TaskConfig:
    name: str
    enable: bool = True

    address_name: str = UNDEFINED
    ipv4: bool = False
    ipv6: bool = False

    domain: str = UNDEFINED
    provider_name: str = UNDEFINED
    provider_auth: str = UNDEFINED


@dataclass
class Config(JSONWizard):
    common: Common = field(default_factory=Common)

    address: list[AddressProviderConfig] = field(default_factory=list)
    task: list[TaskConfig] = field(default_factory=list)

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

    def update_from_env(self):
        self.common.sentry_dsn = env.SENTRY_DSN


_config: Config = Config()


def reinit_config_from_dict(data: dict):
    global _config

    logger.debug("Load config value from python object(dict)")
    _config = Config.from_dict(data)
    _config.update_from_env()


def reinit_config_from_file(file_name: str):
    logger.info(f"Config: Open file {file_name}...")
    try:
        with open(file_name, "rb") as f:
            data = tomllib.load(f)

    except FileNotFoundError as e:
        message = f"Config: Open file {file_name} failed, {e}"
        logger.critical(message)
        raise ConfigException(message)

    except tomllib.TOMLDecodeError as e:
        message = f"Config: Parse file {file_name} failed, {e}"
        logger.critical(message)
        raise ConfigException(message)

    reinit_config_from_dict(data)


@ttl_cache(ttl=60)
def get_config(config_toml: str | None = None) -> Config:
    if config_toml is None:
        config_toml = env.CONFIG_TOML

    reinit_config_from_file(config_toml)

    return _config
