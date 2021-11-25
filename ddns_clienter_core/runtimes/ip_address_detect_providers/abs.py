from typing import Optional
import re


from ddns_clienter_core.runtimes.config import Address


class ExceptionIPAddressDetect(Exception):
    pass


class DetectAddressProviderAbs:
    _address_info: Address

    ipv4_address = None
    ipv6_address = None

    def __init__(self, address_info: Address):
        self._address_info = address_info
        self._detect_ip_address()

    @property
    def name(self):
        raise NotImplemented

    def _match_ipv4(self, ip_address: str) -> bool:
        if re.match(self._address_info.ipv4_match_rule, ip_address) is None:
            return False

        return True

    def _match_ipv6(self, ip_address: str) -> bool:
        if re.match(self._address_info.ipv6_match_rule, ip_address) is None:
            return False

        return True

    def _detect_ip_address(self):
        raise NotImplemented

    def __repr__(self):
        return "{}:{} {}".format(self.name, self.ipv4_address, self.ipv6_address)
