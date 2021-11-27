from ddns_clienter_core import models
from ddns_clienter_core.runtimes import config
from ddns_clienter_core.runtimes.dns_providers.dynv6 import DDNSProviderDynv6


def push_address_to_dns_provider(config_domain: config.Domain, real_push: bool = True):
    db_address = models.Address.objects.filter(name=config_domain.address_name).first()

    if config_domain.provider == "dynv6":
        provider_class = DDNSProviderDynv6

    else:
        raise

    provider = provider_class(
        config_domain, db_address.ipv4_address, db_address.ipv6_address, real_push
    )
    provider.update_to_db()
    return
