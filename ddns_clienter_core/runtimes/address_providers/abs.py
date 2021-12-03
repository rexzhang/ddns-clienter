from typing import Optional
import re

from ddns_clienter_core.runtimes import config


class AddressProviderException(Exception):
    pass


class AddressProviderAbs:
    ipv4_address: Optional[str] = None
    ipv6_address: Optional[str] = None

    changed_address_s_id: Optional[int] = None

    def __init__(self, config_address: config.ConfigAddress):
        self._config_address = config_address
        self._detect_ip_address()

    @property
    def name(self):
        raise NotImplemented

    def _match_ipv4(self, ip_address: str) -> bool:
        if re.match(self._config_address.ipv4_match_rule, ip_address) is None:
            return False

        return True

    def _match_ipv6(self, ip_address: str) -> bool:
        if re.match(self._config_address.ipv6_match_rule, ip_address) is None:
            return False

        return True

    def _detect_ip_address(self) -> None:
        raise NotImplemented

    def __repr__(self):
        return "{}:{} {}".format(self.name, self.ipv4_address, self.ipv6_address)
