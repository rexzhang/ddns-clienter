import re
from ipaddress import ip_address as ip_address_string_check
from logging import getLogger

import httpx

from ddns_clienter.core.runtimes.address_providers.abs import AddressProviderAbs
from ddns_clienter.core.runtimes.event import event

logger = getLogger(__name__)


def pick_out_ip_address(ipv: int, text: str) -> str:
    if ipv == 4:
        ip_regex = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
    else:
        ip_regex = r"(?<![:.\w])(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}(?![:.\w])"
    ip_list = re.findall(ip_regex, text)
    if len(ip_list) == 0:
        return ""

    return ip_list[0]


class AddressProviderHttpGetAbs(AddressProviderAbs):
    name = "abs"
    url_ipv4 = None
    url_ipv6 = None
    user_agent: str | None = None

    @staticmethod
    async def _logging_error_message(message):
        logger.error(message)
        await event.error(message)

    async def _detect_with_http_get(self, ipv: int) -> str | None:
        if ipv == 4:
            url = self.url_ipv4
        elif ipv == 6:
            url = self.url_ipv6
        else:
            raise

        if self.user_agent is None:
            headers = None
        else:
            headers = {"User-Agent": self.user_agent, "Cache-Control": "no-cache"}

        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(url, headers=headers)
        except httpx.HTTPError as e:
            await self._logging_error_message(
                f"Detect IP Address failed; bad responds; provider:[{self.name}], IPv{ipv}, message:{e}"
            )
            return None

        if r.status_code != 200:
            await self._logging_error_message(
                f"Detect IP Address failed; bad responds; provider:[{self.name}], IPv{ipv}, status_code:{r.status_code}!=200"
            )
            return None

        ip_address = pick_out_ip_address(ipv, r.text)
        if len(ip_address) == 0:
            await self._logging_error_message(
                f"Detect IP Address failed; bad content; provider:[{self.name}], IPv{ipv}, bad ip address:{ip_address}"
            )
            return None

        try:
            ip_address_string_check(ip_address)

        except ValueError as e:
            await self._logging_error_message(
                f"Detect IP Address failed; bad content; provider:[{self.name}], IPv{ipv}, message:{e}"
            )
            return None

        return ip_address

    async def _get_address(
        self, ipv4: bool, ipv6: bool, parameter: str
    ) -> tuple[list[str], list[str]]:
        ipv4_addresses = list()
        ipv6_addresses = list()

        if ipv4 and self.url_ipv4:
            ip_address = await self._detect_with_http_get(4)
            if ip_address is not None:
                ipv4_addresses.append(ip_address)

        if ipv6 and self.url_ipv6:
            ip_address = await self._detect_with_http_get(6)
            if ip_address is not None:
                ipv6_addresses.append(ip_address)

        return ipv4_addresses, ipv6_addresses


class AddressProviderIpify(AddressProviderHttpGetAbs):
    name = "ipify"
    url_ipv4 = "https://api4.ipify.org/"
    url_ipv6 = "http://api6.ipify.org/"


class AddressProviderNoip(AddressProviderHttpGetAbs):
    name = "noip"
    url_ipv4 = "https://ip1.dynupdate.no-ip.com/"
    url_ipv6 = "http://ip1.dynupdate6.no-ip.com/"


class AddressProviderIpip(AddressProviderHttpGetAbs):
    # https://www.ipip.net/myip.html
    name = "ipip"
    url_ipv4 = "http://myip.ipip.net"


class AddressProviderMyipLa(AddressProviderHttpGetAbs):
    # https://www.ipip.net/myip.html
    name = "myip.la"
    url_ipv4 = "https://myip.la"


class AddressProviderCipCc(AddressProviderHttpGetAbs):
    name = "cip.cc"
    url_ipv4 = "http://www.cip.cc/"
    user_agent = "curl/7.88.1"


class AddressProviderNetCn(AddressProviderHttpGetAbs):
    name = "net.cn"
    url_ipv4 = "http://www.net.cn/static/customercare/yourip.asp"
