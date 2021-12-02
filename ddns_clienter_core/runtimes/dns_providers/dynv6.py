from typing import Optional
import dataclasses
from logging import getLogger

import requests
from django.utils import timezone

from ddns_clienter_core import models
from ddns_clienter_core.runtimes import config

logger = getLogger(__name__)


class DDNSProviderException(Exception):
    pass


class DDNSProvider:
    _push_success: bool

    def __init__(
        self,
        config_domain: config.Domain,
        ipv4_address: Optional[str],
        ipv6_address: Optional[str],
        real_push: bool,
    ):
        self._config_domain = config_domain

        if self._config_domain.ipv4 and ipv4_address:
            self._ipv4_address = ipv4_address
        else:
            self._ipv4_address = None

        if self._config_domain.ipv6 and ipv6_address:
            self._ipv6_address = ipv6_address
        else:
            self._ipv6_address = None

        self._real_push = real_push

        self._push_to_provider()

    def _push_to_provider(self):
        raise NotImplemented

    def update_to_db(self):
        db_domain = models.Domain.objects.filter(name=self._config_domain.name).first()
        if db_domain is None:
            db_domain = models.Domain(**dataclasses.asdict(self._config_domain))

        if self._push_success:
            db_domain.last_ip_addresses = db_domain.ip_addresses

            if self._ipv4_address is not None:
                db_domain.ip_addresses = self._ipv4_address
            else:
                db_domain.ip_addresses = ""
            if self._ipv6_address is not None:
                if len(db_domain.ip_addresses) != 0:
                    db_domain.ip_addresses += ","
                db_domain.ip_addresses += self._ipv6_address

            db_domain.ip_addresses_is_up_to_date = True
        else:
            db_domain.ip_addresses_is_up_to_date = False

        db_domain.save()


class DDNSProviderDynv6(DDNSProvider):
    _update_api_url: str = "https://dynv6.com/api/update"

    def _push_to_provider(self):
        params = {
            "zone": self._config_domain.domain,
            "token": self._config_domain.provider_token,
        }
        if self._config_domain.ipv4 and self._ipv4_address:
            params.update({"ipv4": self._ipv4_address})
        if self._config_domain.ipv6 and self._ipv6_address:
            params.update({"ipv6": self._ipv6_address})

        logger.debug(params)
        if self._real_push:
            r = requests.get(self._update_api_url, params)
            logger.info(r)
            status_code = r.status_code
        else:
            status_code = 200

        if status_code == 200:
            self._push_success = True
        else:
            self._push_success = False
