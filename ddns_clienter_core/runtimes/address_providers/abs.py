import ipaddress
import re
from logging import getLogger

from ddns_clienter_core.constants import AddressInfo
from ddns_clienter_core.runtimes import config

logger = getLogger(__name__)


class AddressProviderException(Exception):
    pass


class AddressProviderAbs:
    name: str | None = None

    def __init__(self):
        if self.name is None:
            raise NotImplementedError("AddressProviderAbs.name")

    async def __call__(
        self, address_provider_config: config.AddressProviderConfig
    ) -> AddressInfo:
        ipv4_addresses, ipv6_addresses = await self._get_address(
            address_provider_config.ipv4,
            address_provider_config.ipv6,
            address_provider_config.provider_parameter,
        )

        ipv4_address = None
        if address_provider_config.ipv4:
            for ip_address in ipv4_addresses:
                obj = self._match_address(
                    ip_address=ip_address,
                    match_rule=address_provider_config.ipv4_match_rule,
                    allow_private=address_provider_config.allow_private,
                    allow_loopback=address_provider_config.allow_loopback,
                )

                if obj is None:
                    continue

                if obj.version != 4:
                    logger.warning(f"{ip_address} is not IPv4")
                    continue

                ipv4_address = obj
                break

        ipv6_address = None
        if address_provider_config.ipv6:
            for ip_address in ipv6_addresses:
                obj = self._match_address(
                    ip_address=ip_address,
                    match_rule=address_provider_config.ipv6_match_rule,
                    allow_private=address_provider_config.allow_private,
                    allow_loopback=address_provider_config.allow_loopback,
                )

                if obj is None:
                    continue

                if obj.version != 6:
                    logger.warning(f"{ip_address} is not IPv6")
                    continue

                ipv6_address = obj
                break

        ipv6_prefix_length = address_provider_config.ipv6_prefix_length

        return AddressInfo(
            ipv4_address=ipv4_address,
            ipv6_address=ipv6_address,
            ipv6_prefix_length=ipv6_prefix_length,
        )

    async def _get_address(
        self, ipv4: bool, ipv6: bool, parameter: str
    ) -> (list[str], list[str]):
        raise NotImplemented

    @staticmethod
    def _match_address(
        ip_address: str,
        match_rule: str,
        allow_private: bool,
        allow_loopback: bool,
    ) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
        if re.match(match_rule, ip_address) is None:
            logger.debug(f"can not match rule:{match_rule}, {ip_address}")
            return None

        try:
            obj = ipaddress.ip_address(ip_address)
        except ValueError as e:
            logger.warning(e)
            return None

        if obj.is_loopback:
            if allow_loopback:
                return obj

            return None

        if obj.is_private:
            if allow_private:
                return obj

            return None

        if obj.is_link_local or obj.is_multicast:
            return None

        return obj

    def __repr__(self):
        return "AddressProvider:{}".format(self.name)
