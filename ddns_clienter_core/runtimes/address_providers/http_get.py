from ipaddress import ip_address as ip_address_string_check
from logging import getLogger

import httpx

from ddns_clienter_core.runtimes.address_providers.abs import AddressProviderAbs
from ddns_clienter_core.runtimes.event import event

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
            await event.error(message)
            return None

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
            ip_address = await self._detect_with_http_get(self._ipv4_url)
            if ip_address is not None:
                ipv4_addresses.append(ip_address)

        if ipv6 and self._ipv6_url:
            ip_address = await self._detect_with_http_get(self._ipv6_url)
            if ip_address is not None:
                ipv6_addresses.append(ip_address)

        return ipv4_addresses, ipv6_addresses


class AddressProviderIpify(AddressProviderHttpGetAbs):
    name = "ipify"

    @property
    def _ipv4_url(self):
        return "http://api4.ipify.org/"

    @property
    def _ipv6_url(self):
        return "http://api64.ipify.org/"
        # return "http://api6.ipify.org/"  # ipv6 only server


class AddressProviderNoip(AddressProviderHttpGetAbs):
    name = "noip"

    @property
    def _ipv4_url(self):
        return "http://ip1.dynupdate.no-ip.com/"

    @property
    def _ipv6_url(self):
        return "http://ip1.dynupdate6.no-ip.com/"
