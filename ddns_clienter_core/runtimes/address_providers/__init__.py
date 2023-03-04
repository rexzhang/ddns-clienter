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

__all__ = ["AddressProviderException", "get_ip_address_from_provider"]

_address_provider_class_mapper = {
    provider_class.name: provider_class
    for provider_class in [
        AddressProviderHostName,
        AddressProviderIpify,
        AddressProviderNoip,
    ]
}


async def get_ip_address_from_provider(
    address_provider_config: config.AddressProviderConfig,
) -> AddressInfo:
    provider_class = _address_provider_class_mapper.get(
        address_provider_config.provider_name
    )
    if provider_class is None:
        raise AddressProviderException(
            f"Can not match AddressProvider:{address_provider_config.provider_name}"
        )

    return await provider_class()(address_provider_config)
