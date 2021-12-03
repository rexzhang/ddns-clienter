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
    ConfigDomain,
    ConfigException,
)
from ddns_clienter_core.runtimes.address_providers import (
    detect_ip_address_from_provider,
    AddressProviderException,
)
from ddns_clienter_core.runtimes.dns_providers import (
    push_address_to_dns_provider,
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
    _address_status: dict[str, AddressChangeStatus] = dict()  # address status

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
        self, config_domain: ConfigDomain
    ) -> (Optional[str], Optional[str]):
        address_status = self._address_status.get(config_domain.address_name)

        db_domain = models.Domain.objects.filter(name=config_domain.name).first()
        if db_domain is None:
            # can't found task record
            return (
                address_status.ipv4_newest_address,
                address_status.ipv6_newest_address,
            )

        if (
            db_domain.last_update_time + timedelta(minutes=settings.PUSH_INTERVALS)
            < timezone.now()
        ):
            # PUSH_INTERVALS timeout
            return (
                address_status.ipv4_newest_address,
                address_status.ipv6_newest_address,
            )

        if db_domain.ipv4 and (
            address_status.ipv4_is_changed or not db_domain.last_update_is_success
        ):
            ipv4_new_address = address_status.ipv4_newest_address
        else:
            ipv4_new_address = None

        if db_domain.ipv6 and (
            address_status.ipv6_is_changed or not db_domain.last_update_is_success
        ):
            ipv6_new_address = address_status.ipv6_newest_address
        else:
            ipv6_new_address = None

        return ipv4_new_address, ipv6_new_address

    @staticmethod
    def update_domain_info_to_db(
        config_domain: ConfigDomain,
        ipv4_new_address: Optional[str],
        ipv6_new_address: Optional[str],
        push_success: bool,
    ):
        db_domain = models.Domain.objects.filter(name=config_domain.name).first()
        if db_domain is None:
            db_domain = models.Domain(**dataclass_asdict(config_domain))

        if push_success:
            new_addresses = str()
            if config_domain.ipv4 and ipv4_new_address is not None:
                new_addresses += ipv4_new_address

            if config_domain.ipv6 and ipv6_new_address is not None:
                if len(new_addresses) != 0:
                    new_addresses += ","

                new_addresses += ipv6_new_address

            db_domain.last_ip_addresses = db_domain.ip_addresses
            db_domain.ip_addresses = new_addresses
            db_domain.last_update_is_success = True
            db_domain.last_update_time = timezone.now()

        else:
            db_domain.last_update_is_success = False

        db_domain.save()


def check_and_push(config_file_name: Optional[str] = None, real_push: bool = True):
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
    for config_domain in config.domains:
        ipv4_newest_address, ipv6_newest_address = master.get_new_addresses(
            config_domain
        )
        if ipv4_newest_address is None and ipv6_newest_address is None:
            logger.debug("Skip task:{}".format(config_domain.name))
            continue

        try:
            push_success = push_address_to_dns_provider(
                config_domain, ipv4_newest_address, ipv6_newest_address, real_push
            )
        except DDNSProviderException as e:
            event.send_event(str(e), level=event.EventLevel.ERROR)
            continue

        master.update_domain_info_to_db(
            config_domain, ipv4_newest_address, ipv6_newest_address, push_success
        )
