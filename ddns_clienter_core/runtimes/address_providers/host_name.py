import asyncio
import socket
from logging import getLogger

from ddns_clienter_core.runtimes.address_providers.abs import (
    AddressProviderAbs,
    AddressProviderException,
)

logger = getLogger(__name__)


class AddressProviderHostName(AddressProviderAbs):
    name = "hostname"

    async def _get_address(
        self, ipv4: bool, ipv6: bool, parameter: str
    ) -> tuple[list[str], list[str]]:
        try:
            loop = asyncio.get_running_loop()
            data = await loop.getaddrinfo(parameter, 80)
        except socket.gaierror as e:
            message = f"Detect IP Address failed, provider:[{self.name}], parameter:{parameter}, message:{e}"
            logger.error(message)
            raise AddressProviderException(message)

        ipv4_addresses = list()
        ipv6_addresses = list()

        for item in data:
            if item[0] == socket.AF_INET and item[1] == socket.SOCK_STREAM and ipv4:
                ip_address = item[4][0]
                ipv4_addresses.append(ip_address)
                continue

            if item[0] == socket.AF_INET6 and item[1] == socket.SOCK_STREAM and ipv6:
                ip_address = item[4][0]
                ipv6_addresses.append(ip_address)
                continue

        return ipv4_addresses, ipv6_addresses
