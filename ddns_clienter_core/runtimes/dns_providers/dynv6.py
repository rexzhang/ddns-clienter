from typing import Optional
from logging import getLogger

import requests

from ddns_clienter_core.runtimes.config import Task

logger = getLogger(__name__)


class DNSProvider:
    def _update(
        self,
        domain: str,
        token: str,
        ip_v4_address: Optional[str],
        ip_v6_address: Optional[str],
    ):
        raise NotImplemented

    def update(self, task: Task, ipv4_address: str, ipv6_address: str):
        if not task.ipv4:
            ipv4_address = None
        if not task.ipv6:
            ipv6_address = None

        self._update(task.domain, task.dns_token, ipv4_address, ipv6_address)


class DNSProviderDynv6(DNSProvider):
    _update_api_url: str = "https://dynv6.com/api/update"

    def _update(
        self,
        domain: str,
        token: str,
        ip_v4_address: Optional[str],
        ip_v6_address: Optional[str],
    ):
        params = {
            "zone": domain,
            "token": token,
        }
        if ip_v4_address:
            params.update({"ipv4": ip_v4_address})
        if ip_v6_address:
            params.update({"ipv6": ip_v6_address})

        logger.debug(params)
        r = requests.get(self._update_api_url, params)
        logger.info(r)
