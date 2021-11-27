from typing import Optional
from ddns_clienter_core.runtimes import config
from ddns_clienter_core.runtimes.address_providers.host_name import (
    AddressProviderHostName,
)
from ddns_clienter_core.runtimes.address_providers.http_get import (
    AddressProviderIpify,
    AddressProviderNoip,
)

__all__ = [
    "detect_ip_address_from_provider",
    "AddressProviderHostName",
    "AddressProviderIpify",
    "AddressProviderNoip",
]


def detect_ip_address_from_provider(address: config.Address) -> Optional[int]:
    if address.provider == "hostname":
        provider = AddressProviderHostName(address)
    elif address.provider == "ipify":
        provider = AddressProviderIpify(address)
    elif address.provider == "noip":
        provider = AddressProviderNoip(address)

    else:
        raise

    provider.update_to_db()
    return provider.changed_address_s_id
