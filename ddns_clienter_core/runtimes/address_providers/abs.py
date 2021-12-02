from typing import Optional
import re
import dataclasses
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from ddns_clienter_core import models
from ddns_clienter_core.runtimes import config


class AddressProviderException(Exception):
    pass


class AddressProviderAbs:
    ipv4_address: Optional[str] = None
    ipv6_address: Optional[str] = None

    changed_address_s_id: Optional[int] = None

    def __init__(self, config_address: config.Address):
        self._config_address = config_address
        self._detect_ip_address()

    @property
    def name(self):
        raise NotImplemented

    def _match_ipv4(self, ip_address: str) -> bool:
        if re.match(self._config_address.ipv4_match_rule, ip_address) is None:
            return False

        return True

    def _match_ipv6(self, ip_address: str) -> bool:
        if re.match(self._config_address.ipv6_match_rule, ip_address) is None:
            return False

        return True

    def _detect_ip_address(self) -> None:
        raise NotImplemented

    @staticmethod
    def _ip_address_s_new_change_time(last_change_time) -> Optional[any]:
        now = timezone.now()
        if last_change_time is None:
            return now

        if last_change_time + timedelta(minutes=settings.PUSH_INTERVALS) > now:
            return None

        return now

    def update_to_db(self) -> None:
        ip_address_is_changed = False
        address = models.Address.objects.filter(name=self._config_address.name).first()
        if address is None:
            address = models.Address(**dataclasses.asdict(self._config_address))

        if self.ipv4_address != address.ipv4_address:
            now = self._ip_address_s_new_change_time(address.ipv4_last_change_time)
            if now is not None:
                address.ipv4_last_address = address.ipv4_address
                address.ipv4_address = self.ipv4_address
                address.ipv4_last_change_time = now

                ip_address_is_changed = True

        if self.ipv4_address != address.ipv6_address:
            now = self._ip_address_s_new_change_time(address.ipv6_last_change_time)
            if now is not None:
                address.ipv6_last_address = address.ipv6_address
                address.ipv6_address = self.ipv6_address
                address.ipv6_last_change_time = now

                ip_address_is_changed = True

        if ip_address_is_changed:
            self.changed_address_s_id = address.id

        address.save()

    def __repr__(self):
        return "{}:{} {}".format(self.name, self.ipv4_address, self.ipv6_address)
