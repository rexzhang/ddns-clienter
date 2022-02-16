from typing import ClassVar
import re
from ipaddress import IPv4Address, IPv6Address, AddressValueError
from logging import getLogger

from ddns_clienter_core.runtimes import config

logger = getLogger(__name__)


class AddressProviderException(Exception):
    pass


class AddressProviderAbs:
    _ipv4_address: IPv4Address | None
    _ipv6_address: IPv6Address | None
    ipv6_prefix: int | None

    changed_address_s_id: int | None = None

    def __init__(self, address_c: config.AddressConfig):
        self._ipv4_address = None
        self._ipv6_address = None
        self.ipv6_prefix = None

        self._address_c = address_c
        self._detect_ip_address()

    @property
    def name(self):
        raise NotImplemented

    @property
    def ipv4_address(self):
        return self._ipv4_address

    @property
    def ipv6_address(self):
        return self._ipv6_address

    def _set_ip_address(
        self, ip_address: str, factory_class: ClassVar, match_rule: str
    ) -> IPv4Address | IPv6Address | None:
        if re.match(match_rule, ip_address) is None:
            logger.warning("can not match rule:{}, {}".format(ip_address, match_rule))
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

        self._ipv4_address = obj
        return True

    def set_ipv6_address(self, ip_address: str) -> bool:
        obj = self._set_ip_address(
            ip_address, IPv6Address, self._address_c.ipv6_match_rule
        )
        if obj is None:
            return False

        self._ipv6_address = obj
        return True

    def _detect_ip_address(self) -> None:
        raise NotImplemented

    def __repr__(self):
        return "{}:{} {}/{}, {}".format(
            self.name,
            self._ipv4_address,
            self._ipv6_address,
            self.ipv6_prefix,
            self._address_c,
        )
