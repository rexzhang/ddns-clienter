from typing import Optional
from logging import getLogger

from django.conf import settings

from ddns_clienter_core.models import Address
from ddns_clienter_core.runtimes.config import Config, ConfigException
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


def check_and_push(config_file_name: Optional[str] = None, real_push: bool = True):
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

    # get ip address, update ip address info into config.addresses
    changed_address_s_ids = list()
    for address_name in config.addresses:
        try:
            address_id = detect_ip_address_from_provider(config.addresses[address_name])
            logger.debug("address_id:{}".format(address_id))
            if address_id is not None:
                changed_address_s_ids.append(address_id)

        except AddressProviderException as e:
            event.send_event(str(e), level=event.EventLevel.ERROR)
    logger.debug("changed_address_s_ids:{}".format(changed_address_s_ids))

    address_names = set(
        Address.objects.filter(id__in=changed_address_s_ids).values_list(
            "name", flat=True
        )
    )
    logger.debug("address_names:{}".format(address_names))

    # put A/AAAA record to DNS provider
    for domain in config.domains:
        if domain.address_name not in address_names:
            continue

        try:
            push_address_to_dns_provider(domain, real_push)
        except DDNSProviderException as e:
            event.send_event(str(e), level=event.EventLevel.ERROR)
