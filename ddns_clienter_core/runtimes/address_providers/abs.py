from typing import ClassVar
import re
from ipaddress import IPv4Address, IPv6Address, AddressValueError
from logging import getLogger

from ddns_clienter_core.constants import AddressInfo
from ddns_clienter_core.runtimes import config

logger = getLogger(__name__)


class AddressProviderException(Exception):
    pass


class AddressProviderAbs:
    ip_address: AddressInfo

    def __init__(self, address_c: config.AddressConfig):
        self.ip_address = AddressInfo()

        self._address_c = address_c
        self._detect_ip_address()

    @property
    def name(self):
        raise NotImplemented

    def _set_ip_address(
        self, ip_address: str, factory_class: ClassVar, match_rule: str
    ) -> IPv4Address | IPv6Address | None:
        if re.match(match_rule, ip_address) is None:
            logger.warning("can not match rule:{}, {}".format(match_rule, ip_address))
            return None

        try:
            obj = factory_class(ip_address)

        except AddressValueError:
            logger.warning("parser address failed, {}".format(ip_address))
            return None

        if obj.is_link_local or obj.is_multicast:
            logger.warning(
                "ip address is_link_local or is_multicast, {}".format(ip_address)
            )
            return None

        if obj.is_loopback and not self._address_c.allow_loopback:
            logger.warning("ip address is_loopback, {}".format(ip_address))
            return None

        if obj.is_private and not self._address_c.allow_private:
            logger.warning("ip address is_private, {}".format(ip_address))
            return None

        return obj

    def set_ipv4_address(self, ip_address: str) -> bool:
        obj = self._set_ip_address(
            ip_address, IPv4Address, self._address_c.ipv4_match_rule
        )
        if obj is None:
            return False

        self.ip_address.ipv4_address = obj
        return True

    def set_ipv6_address(self, ip_address: str) -> bool:
        obj = self._set_ip_address(
            ip_address, IPv6Address, self._address_c.ipv6_match_rule
        )
        if obj is None:
            return False

        self.ip_address.ipv6_address = obj
        return True

    def _detect_ip_address(self) -> None:
        raise NotImplemented

    def __repr__(self):
        return "{}:{} {}/{}, {}".format(
            self.name,
            self.ip_address.ipv4_address,
            self.ip_address.ipv6_address,
            self.ip_address.ipv6_prefix_length,
            self._address_c,
        )
