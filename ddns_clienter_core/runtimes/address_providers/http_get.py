from typing import Optional, Callable
from ipaddress import ip_address as ip_address_string_check
from logging import getLogger

import requests

from .abs import AddressProviderAbs

logger = getLogger(__name__)


class AddressProviderHttpGetAbs(AddressProviderAbs):
    @property
    def _ipv4_url(self):
        raise NotImplemented

    @property
    def _ipv6_url(self):
        raise NotImplemented

    @staticmethod
    def _detect_process(server_url: str, match_func: Callable) -> Optional[str]:

        r = requests.get(server_url)
        if r.status_code != 200:
            return None

        ip_address = r.text.rstrip("\n ")
        if len(ip_address) == 0:
            return None

        try:
            ip_address_string_check(ip_address)

        except ValueError:
            return None

        if not match_func(ip_address):
            return None

        return ip_address

    def _detect_ip_address(self) -> None:
        if self._config_address.ipv4 and self._ipv4_url:
            self.ipv4_address = self._detect_process(self._ipv4_url, self._match_ipv4)

        if self._config_address.ipv6:
            self.ipv6_address = self._detect_process(self._ipv6_url, self._match_ipv6)


class AddressProviderIpify(AddressProviderHttpGetAbs):
    @property
    def name(self):
        return "ipify"

    @property
    def _ipv4_url(self):
        return "https://api.ipify.org/"

    @property
    def _ipv6_url(self):
        return "https://api6.ipify.org/"


class AddressProviderNoip(AddressProviderHttpGetAbs):
    @property
    def name(self):
        return "noip"

    @property
    def _ipv4_url(self):
        return "https://api.ipify.org/"

    @property
    def _ipv6_url(self):
        return "https://api6.ipify.org/"
