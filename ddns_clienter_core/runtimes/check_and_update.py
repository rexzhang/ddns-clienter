from typing import Optional
from dataclasses import dataclass, asdict as dataclass_asdict
from datetime import timedelta
from logging import getLogger

from django.conf import settings
from django.utils import timezone

from ddns_clienter_core import models
from ddns_clienter_core.runtimes.config import (
    Config,
    ConfigAddress,
    ConfigTask,
    ConfigException,
)
from ddns_clienter_core.runtimes.address_providers import (
    detect_ip_address_from_provider,
    AddressProviderException,
)
from ddns_clienter_core.runtimes.dns_providers import (
    update_address_to_dns_provider,
    DDNSProviderException,
)
from ddns_clienter_core.runtimes import event

logger = getLogger(__name__)


@dataclass
class AddressChangeStatus:
    address_config: ConfigAddress
    ipv4_is_changed: bool
    ipv6_is_changed: bool
    ipv4_newest_address: Optional[str]
    ipv6_newest_address: Optional[str]


class AddressChangeMaster:
    _address_status: dict[str, AddressChangeStatus]  # address status

    def __init__(self):
        self._address_status = dict()

    def import_address_info(
        self,
        config_address: ConfigAddress,
        ipv4_newest_address: Optional[str],
        ipv6_newest_address: Optional[str],
    ):
        # xxx_new_address: None == no changed == no checked

        db_address = models.Address.objects.filter(name=config_address.name).first()
        if db_address is None:
            db_address = models.Address(**dataclass_asdict(config_address))

        # maybe address config changed, force update address info to db
        db_address.provider = config_address.provider
        db_address.parameter = config_address.parameter
        db_address.ipv4 = config_address.ipv4
        db_address.ipv6 = config_address.ipv6
        db_address.ipv4_match_rule = config_address.ipv4_match_rule
        db_address.ipv6_match_rule = config_address.ipv6_match_rule

        now = timezone.now()
        if (
            ipv4_newest_address is not None
            and ipv4_newest_address != db_address.ipv4_address
        ):
            db_address.ipv4_last_address = db_address.ipv4_address
            db_address.ipv4_address = ipv4_newest_address
            db_address.ipv4_last_change_time = now

            ipv4_is_changed = True
        else:
            ipv4_is_changed = False

        if (
            ipv6_newest_address is not None
            and ipv6_newest_address != db_address.ipv6_address
        ):
            db_address.ipv6_last_address = db_address.ipv6_address
            db_address.ipv6_address = ipv6_newest_address
            db_address.ipv6_last_change_time = now

            ipv6_is_changed = True
        else:
            ipv6_is_changed = False

        self._address_status.update(
            {
                config_address.name: AddressChangeStatus(
                    config_address,
                    ipv4_is_changed,
                    ipv6_is_changed,
                    ipv4_newest_address,
                    ipv6_newest_address,
                )
            }
        )

        db_address.save()

    def get_new_addresses(
        self, config_task: ConfigTask
    ) -> (Optional[str], Optional[str], bool):
        address_status = self._address_status.get(config_task.address_name)

        db_task = models.Task.objects.filter(name=config_task.name).first()
        if db_task is None:
            # can't found task record
            return (
                address_status.ipv4_newest_address,
                address_status.ipv6_newest_address,
                False,
            )

        if (
            db_task.last_update_time + timedelta(minutes=settings.PUSH_INTERVALS)
            < timezone.now()
        ):
            # PUSH_INTERVALS timeout
            return (
                address_status.ipv4_newest_address,
                address_status.ipv6_newest_address,
                False,
            )

        if (
            (config_task.provider != db_task.provider)
            or (config_task.provider_token != db_task.provider_token)
            or (config_task.domain != db_task.domain)
            or (config_task.host != db_task.host)
            or (config_task.address_name != db_task.address_name)
            or (config_task.ipv4 != db_task.ipv4)
            or (config_task.ipv6 != db_task.ipv6)
        ):
            # task config changed
            return (
                address_status.ipv4_newest_address,
                address_status.ipv6_newest_address,
                True,
            )

        if db_task.ipv4 and (
            address_status.ipv4_is_changed or not db_task.last_update_is_success
        ):
            ipv4_new_address = address_status.ipv4_newest_address
        else:
            ipv4_new_address = None

        if db_task.ipv6 and (
            address_status.ipv6_is_changed or not db_task.last_update_is_success
        ):
            ipv6_new_address = address_status.ipv6_newest_address
        else:
            ipv6_new_address = None

        return ipv4_new_address, ipv6_new_address, False

    @staticmethod
    def update_task_skipped_to_db(config_task: ConfigTask):
        db_task = models.Task.objects.filter(name=config_task.name).first()
        db_task.save()

    @staticmethod
    def update_task_success_to_db(
        config_task: ConfigTask,
        ipv4_new_address: Optional[str],
        ipv6_new_address: Optional[str],
        task_success: bool,
        task_config_changed: bool,
    ):
        db_task = models.Task.objects.filter(name=config_task.name).first()
        if db_task is None:
            db_task = models.Task(**dataclass_asdict(config_task))

        if task_config_changed:
            db_task.provider = config_task.provider
            db_task.provider_token = config_task.provider_token
            db_task.domain = config_task.domain
            db_task.host = config_task.host
            db_task.address_name = config_task.address_name
            db_task.ipv4 = config_task.ipv4
            db_task.ipv6 = config_task.ipv6

        if task_success:
            new_addresses = str()
            if config_task.ipv4 and ipv4_new_address is not None:
                new_addresses += ipv4_new_address

            if config_task.ipv6 and ipv6_new_address is not None:
                if len(new_addresses) != 0:
                    new_addresses += ","

                new_addresses += ipv6_new_address

            db_task.last_ip_addresses = db_task.ip_addresses
            db_task.ip_addresses = new_addresses
            db_task.last_update_is_success = True
            db_task.last_update_time = timezone.now()

        else:
            db_task.last_update_is_success = False

        db_task.save()


def check_and_update(config_file_name: Optional[str] = None, real_push: bool = True):
    # load config
    if config_file_name is None:
        config_file_name = settings.BASE_DATA_DIR.joinpath(
            settings.CONFIG_FILE_NAME
        ).as_posix()
    logger.debug("config_file_name:{}".format(config_file_name))

    try:
        config = Config(config_file_name)
    except ConfigException as e:
        event.send_event(str(e), level=event.EventLevel.CRITICAL)
        return
    logger.debug("config:{}".format(config.addresses))

    # prepare
    master = AddressChangeMaster()

    # get ip address, update ip address info into config.addresses
    for config_address in config.addresses.values():
        try:
            ipv4_newest_address, ipv6_newest_address = detect_ip_address_from_provider(
                config_address
            )

        except AddressProviderException as e:
            event.send_event(str(e), level=event.EventLevel.ERROR)
            continue

        logger.debug(
            "Address name:{}, ipv4:{} ipv6:{}".format(
                config_address.name, ipv4_newest_address, ipv6_newest_address
            )
        )
        master.import_address_info(
            config_address, ipv4_newest_address, ipv6_newest_address
        )

    # put A/AAAA record to DNS provider
    for config_task in config.tasks:
        (
            ipv4_newest_address,
            ipv6_newest_address,
            task_config_changed,
        ) = master.get_new_addresses(config_task)
        if ipv4_newest_address is None and ipv6_newest_address is None:
            master.update_task_skipped_to_db(config_task)

            logger.debug("Skip task:{}".format(config_task.name))
            continue

        try:
            task_success = update_address_to_dns_provider(
                config_task, ipv4_newest_address, ipv6_newest_address, real_push
            )
        except DDNSProviderException as e:
            event.send_event(str(e), level=event.EventLevel.ERROR)
            continue

        master.update_task_success_to_db(
            config_task,
            ipv4_newest_address,
            ipv6_newest_address,
            task_success,
            task_config_changed,
        )
