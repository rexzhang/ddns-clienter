from ddns_clienter_core.runtimes.config import Address
from ddns_clienter_core.runtimes.ip_address_detect_providers.host_name import (
    DetectAddressProviderHostName,
)
from ddns_clienter_core.runtimes.ip_address_detect_providers.http_get import (
    DetectAddressProviderIpify,
    DetectAddressProviderNoip,
)

__all__ = [
    "detect_ip_address",
    "DetectAddressProviderHostName",
    "DetectAddressProviderIpify",
    "DetectAddressProviderNoip",
]


def detect_ip_address(address_info: Address) -> (str, str):
    if address_info.provider == "hostname":
        detect = DetectAddressProviderHostName(address_info)
    elif address_info.provider == "ipify":
        detect = DetectAddressProviderIpify(address_info)
    elif address_info.provider == "noip":
        detect = DetectAddressProviderNoip(address_info)
    else:
        raise

    return detect.ipv4_address, detect.ipv6_address
