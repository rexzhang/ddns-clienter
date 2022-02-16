from ddns_clienter_core.constants import AddressInfo
from ddns_clienter_core.runtimes import config
from ddns_clienter_core.runtimes.address_providers.abs import AddressProviderException
from ddns_clienter_core.runtimes.address_providers.host_name import (
    AddressProviderHostName,
)
from ddns_clienter_core.runtimes.address_providers.http_get import (
    AddressProviderIpify,
    AddressProviderNoip,
)

__all__ = [
    "AddressProviderException",
    "get_ip_address_from_provider",
    "AddressProviderHostName",
    "AddressProviderIpify",
    "AddressProviderNoip",
]


def get_ip_address_from_provider(
    address_config: config.AddressConfig,
) -> AddressInfo:
    if address_config.provider == "hostname":
        provider_class = AddressProviderHostName
    elif address_config.provider == "ipify":
        provider_class = AddressProviderIpify
    elif address_config.provider == "noip":
        provider_class = AddressProviderNoip

    else:
        raise

    provider = provider_class(address_config)
    return provider.ip_address
