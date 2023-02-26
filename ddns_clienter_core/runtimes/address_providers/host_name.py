import socket
from logging import getLogger

from .abs import AddressProviderAbs, AddressProviderException

logger = getLogger(__name__)


class AddressProviderHostName(AddressProviderAbs):
    @property
    def name(self):
        return "hostname"

    async def _detect_ip_address(self) -> None:
        try:
            data = socket.getaddrinfo(self._address_c.parameter, 80)
        except socket.gaierror as e:
            message = "Detect IP Address failed, hostname:'{}', message:{}".format(
                self._address_c.parameter, e
            )
            logger.error(message)
            raise AddressProviderException(message)

        for item in data:
            if (
                item[0] == socket.AF_INET
                and item[1] == socket.SOCK_STREAM
                and self._address_c.ipv4
            ):
                ip_address = item[4][0]
                self.set_ipv4_address(ip_address)
                continue

            if (
                item[0] == socket.AF_INET6
                and item[1] == socket.SOCK_STREAM
                and self._address_c.ipv6
            ):
                ip_address = item[4][0]
                self.set_ipv6_address(ip_address)
                continue
