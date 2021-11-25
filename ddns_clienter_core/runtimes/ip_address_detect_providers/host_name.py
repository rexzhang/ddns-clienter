import socket
from logging import getLogger

from ddns_clienter_core.runtimes.ip_address_detect_providers.abs import (
    DetectAddressProviderAbs,
)

logger = getLogger(__name__)


class DetectAddressProviderHostName(DetectAddressProviderAbs):
    @property
    def name(self):
        return "hostname"

    def _detect_ip_address(self):
        try:
            data = socket.getaddrinfo(self._address_info.parameter, 80)
        except socket.gaierror as e:
            logger.error(
                "Detect IP Address failed, hostname:'{}', message:{}".format(
                    self._address_info.parameter, e
                )
            )
            return

        for item in data:
            if (
                item[0] == socket.AF_INET
                and item[1] == socket.SOCK_STREAM
                and self._address_info.ipv4
            ):
                ip_address = item[4][0]
                if not self._match_ipv4(ip_address):
                    continue

                self.ipv4_address = ip_address

            elif (
                item[0] == socket.AF_INET6
                and item[1] == socket.SOCK_STREAM
                and self._address_info.ipv6
            ):
                ip_address = item[4][0]
                if not self._match_ipv6(ip_address):
                    continue

                self.ipv6_address = ip_address
