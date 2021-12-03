from typing import Optional
from logging import getLogger

import requests

from ddns_clienter_core.runtimes import config

logger = getLogger(__name__)


class DDNSProviderException(Exception):
    pass


class DDNSProvider:
    push_success: bool

    def __init__(
        self,
        config_task: config.ConfigTask,
        ipv4_address: Optional[str],
        ipv6_address: Optional[str],
        real_push: bool,
    ):
        self._config_task = config_task

        if self._config_task.ipv4 and ipv4_address:
            self._ipv4_address = ipv4_address
        else:
            self._ipv4_address = None

        if self._config_task.ipv6 and ipv6_address:
            self._ipv6_address = ipv6_address
        else:
            self._ipv6_address = None

        self._real_push = real_push

        self._push_to_provider()

    def _push_to_provider(self):
        raise NotImplemented


class DDNSProviderDynv6(DDNSProvider):
    _update_api_url: str = "https://dynv6.com/api/update"

    def _push_to_provider(self):
        params = {
            "zone": self._config_task.domain,
            "token": self._config_task.provider_token,
        }
        if self._config_task.ipv4 and self._ipv4_address:
            params.update({"ipv4": self._ipv4_address})
        if self._config_task.ipv6 and self._ipv6_address:
            params.update({"ipv6": self._ipv6_address})

        logger.debug(params)
        if self._real_push:
            r = requests.get(self._update_api_url, params)
            logger.info(r)
            status_code = r.status_code
        else:
            status_code = 200

        if status_code == 200:
            self.push_success = True
        else:
            self.push_success = False
