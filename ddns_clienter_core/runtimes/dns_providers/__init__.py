from ddns_clienter_core.runtimes import config
from ddns_clienter_core.runtimes.dns_providers.dynv6 import (
    DDNSProviderDynv6,
    DDNSProviderException,
)

__all__ = ["DDNSProviderException", "push_address_to_dns_provider"]


def push_address_to_dns_provider(
    config_domain: config.ConfigDomain,
    ipv4_address: str,
    ipv6_address: str,
    real_push: bool = True,
):
    if config_domain.provider == "dynv6":
        provider_class = DDNSProviderDynv6

    else:
        raise DDNSProviderException("Can not match DNS provider")

    provider = provider_class(config_domain, ipv4_address, ipv6_address, real_push)
    return provider.push_success
