from ddns_clienter_core.runtimes.config import Config, Address
from ddns_clienter_core.runtimes.ip_address_detect_providers.hostname import (
    IPAddressDetectProviderHostName,
)

__all__ = ["IPAddressDetectProviderHostName", "get_ip_address"]


def get_ip_address(address_info: Address) -> (str, str):
    detect = IPAddressDetectProviderHostName(address_info)
    detect.get_ip_address()
    return detect.ipv4_address, detect.ipv6_address
