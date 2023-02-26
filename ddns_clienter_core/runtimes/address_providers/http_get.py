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

    @staticmethod
    async def _detect_with_http_get(server_url: str) -> str | None:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(server_url)
        except httpx.HTTPError as e:
            raise AddressProviderException(e)

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

    async def _detect_ip_address(self) -> None:
        if self._address_c.ipv4 and self._ipv4_url:
            self.set_ipv4_address(await self._detect_with_http_get(self._ipv4_url))

        if self._address_c.ipv6:
            self.set_ipv6_address(await self._detect_with_http_get(self._ipv6_url))


class AddressProviderIpify(AddressProviderHttpGetAbs):
    @property
    def name(self):
        return "ipify"

    @property
    def _ipv4_url(self):
        return "https://api.ipify.org/"

    @property
    def _ipv6_url(self):
        return "https://api64.ipify.org/"
        # return "https://api6.ipify.org/" # ipv6 only server


class AddressProviderNoip(AddressProviderHttpGetAbs):
    @property
    def name(self):
        return "noip"

    @property
    def _ipv4_url(self):
        return "http://ip1.dynupdate.no-ip.com/"

    @property
    def _ipv6_url(self):
        return "http://ip1.dynupdate6.no-ip.com/"
