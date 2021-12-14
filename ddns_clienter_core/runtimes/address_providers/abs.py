import re

from ddns_clienter_core.runtimes import config


class AddressProviderException(Exception):
    pass


class AddressProviderAbs:
    ipv4_address: str | None
    ipv6_address: str | None
    ipv6_prefix: int | None

    changed_address_s_id: int | None = None

    def __init__(self, address_c: config.AddressConfig):
        self.ipv4_address = None
        self.ipv6_address = None
        self.ipv6_prefix = None

        self._address_c = address_c
        self._detect_ip_address()

    @property
    def name(self):
        raise NotImplemented

    def _match_ipv4(self, ip_address: str) -> bool:
        if re.match(self._address_c.ipv4_match_rule, ip_address) is None:
            return False

        return True

    def _match_ipv6(self, ip_address: str) -> bool:
        if re.match(self._address_c.ipv6_match_rule, ip_address) is None:
            return False

        return True

    def _detect_ip_address(self) -> None:
        raise NotImplemented

    def __repr__(self):
        return "{}:{} {}/{}".format(
            self.name, self.ipv4_address, self.ipv6_address, self.ipv6_prefix
        )
