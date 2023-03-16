from ipaddress import ip_address as ip_address_string_check
from logging import getLogger

import httpx

from ddns_clienter_core.runtimes.address_providers.abs import AddressProviderAbs
from ddns_clienter_core.runtimes.event import event

logger = getLogger(__name__)


class AddressProviderHttpGetAbs(AddressProviderAbs):
    name = "abs"
    ipv4_url: str | None = None
    ipv6_url: str | None = None

    @staticmethod
    async def _logging_error_message(message):
        logger.error(message)
        await event.error(message)

    async def _detect_with_http_get(self, server_url: str) -> str | None:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(server_url)
        except httpx.HTTPError as e:
            await self._logging_error_message(
                f"Detect IP Address failed; provider:{self.name}, url:{server_url}, message:{e}"
            )
            return None

        if r.status_code != 200:
            await self._logging_error_message(
                f"Detect IP Address failed; provider:{self.name}, url:{server_url}, status_code{r.status_code}!=200"
            )
            return None

        ip_address = r.text.rstrip("\n ")
        if len(ip_address) == 0:
            await self._logging_error_message(
                f"Detect IP Address failed; provider:{self.name}, url:{server_url}, bad ip address:{ip_address}"
            )
            return None

        try:
            ip_address_string_check(ip_address)

        except ValueError as e:
            await self._logging_error_message(
                f"Detect IP Address failed; provider:{self.name}, url:{server_url}, message:{e}"
            )
            return None

        return ip_address

    async def _get_address(
        self, ipv4: bool, ipv6: bool, parameter: str
    ) -> (list[str], list[str]):
        ipv4_addresses = list()
        ipv6_addresses = list()

        if ipv4 and self.ipv4_url:
            ip_address = await self._detect_with_http_get(self.ipv4_url)
            if ip_address is not None:
                ipv4_addresses.append(ip_address)

        if ipv6 and self.ipv6_url:
            ip_address = await self._detect_with_http_get(self.ipv6_url)
            if ip_address is not None:
                ipv6_addresses.append(ip_address)

        return ipv4_addresses, ipv6_addresses


class AddressProviderIpify(AddressProviderHttpGetAbs):
    name = "ipify"
    ipv4_url: str | None = "http://api4.ipify.org/"
    ipv6_url: str | None = "http://api6.ipify.org/"


class AddressProviderNoip(AddressProviderHttpGetAbs):
    name = "noip"
    ipv4_url: str | None = "http://ip1.dynupdate.no-ip.com/"
    ipv6_url: str | None = "http://ip1.dynupdate6.no-ip.com/"
