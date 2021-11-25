from ddns_clienter_core.runtimes.config import Address
from ddns_clienter_core.runtimes.ip_address_detect_providers.hostname import (
    IPAddressDetectProviderHostName,
)

__all__ = ["IPAddressDetectProviderHostName", "detect_ip_address"]


def detect_ip_address(address_info: Address) -> (str, str):
    detect = IPAddressDetectProviderHostName(address_info)
    return detect.ipv4_address, detect.ipv6_address
