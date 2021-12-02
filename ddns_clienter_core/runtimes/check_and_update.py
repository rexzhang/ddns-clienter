from ddns_clienter_core.models import Address
from ddns_clienter_core.runtimes.config import Config, ConfigException
from ddns_clienter_core.runtimes.address_providers import (
    detect_ip_address_from_provider,
)
from ddns_clienter_core.runtimes.dns_providers import push_address_to_dns_provider
from ddns_clienter_core.runtimes import event


def check_and_push(config_file: str, send_event: bool, real_push: bool = True):
    try:
        config = Config(config_file)
    except ConfigException as e:
        if send_event:
            event.send_event(str(e), level=event.EventLevel.CRITICAL)
        return

    # get ip address, update ip address info into config.addresses
    changed_address_s_ids = list()
    for address_name in config.addresses:
        address_id = detect_ip_address_from_provider(config.addresses[address_name])
        if address_id is not None:
            changed_address_s_ids.append(address_id)

    address_names = set(
        Address.objects.filter(id__in=changed_address_s_ids).values_list(
            "name", flat=True
        )
    )

    # put A/AAAA record to DNS provider
    for domain in config.domains:
        if domain.address_name not in address_names:
            continue

        push_address_to_dns_provider(domain, real_push)
