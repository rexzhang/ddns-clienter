from ipaddress import ip_address as ip_address_string_check
from logging import getLogger

import httpx

from .abs import AddressProviderAbs, AddressProviderException

logger = getLogger(__name__)


class AddressProviderHttpGetAbs(AddressProviderAbs):
    @property
    def _ipv4_url(self):
        raise NotImplemented

    @property
    def _ipv6_url(self):
        raise NotImplemented

    async def _detect_with_http_get(self, server_url: str) -> str | None:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(server_url)
        except httpx.HTTPError as e:
            message = f"Detect IP Address failed, provider:{self.name}, message:{e}"
            logger.error(message)
            raise AddressProviderException(message)

        if r.status_code != 200:
            return None

        ip_address = r.text.rstrip("\n ")
        if len(ip_address) == 0:
            return None

        try:
            ip_address_string_check(ip_address)

        except ValueError:
            return None

        return ip_address

    async def _get_address(
        self, ipv4: bool, ipv6: bool, parameter: str
    ) -> (list[str], list[str]):
        ipv4_addresses = list()
        ipv6_addresses = list()

        if ipv4 and self._ipv4_url:
            ipv4_addresses.append(await self._detect_with_http_get(self._ipv4_url))

        if ipv6 and self._ipv6_url:
            ipv6_addresses.append(await self._detect_with_http_get(self._ipv6_url))

        return ipv4_addresses, ipv6_addresses


class AddressProviderIpify(AddressProviderHttpGetAbs):
    name = "ipify"

    @property
    def _ipv4_url(self):
        return "https://api.ipify.org/"

    @property
    def _ipv6_url(self):
        return "https://api64.ipify.org/"
        # return "https://api6.ipify.org/"  # ipv6 only server


class AddressProviderNoip(AddressProviderHttpGetAbs):
    name = "noip"

    @property
    def _ipv4_url(self):
        return "http://ip1.dynupdate.no-ip.com/"

    @property
    def _ipv6_url(self):
        return "http://ip1.dynupdate6.no-ip.com/"
