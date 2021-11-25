import socket
import re
from logging import getLogger

from ddns_clienter_core.runtimes.config import Address


class ExceptionIPAddressDetect(Exception):
    pass


logger = getLogger(__name__)


class IPAddressDetectProviderAbc:
    address_info: Address

    ipv4_address = None
    ipv6_address = None

    def __init__(self, address_info: Address):
        self.address_info = address_info
        self._detect_ip_address()

    @property
    def name(self):
        raise NotImplemented

    def _detect_ip_address(self):
        raise NotImplemented

    def __repr__(self):
        return "{}:{} {}".format(self.name, self.ipv4_address, self.ipv6_address)


class IPAddressDetectProviderHostName(IPAddressDetectProviderAbc):
    @property
    def name(self):
        return "hostname"

    def _detect_ip_address(self):
        try:
            data = socket.getaddrinfo(self.address_info.parameter, 80)
        except socket.gaierror as e:
            logger.error(
                "Detect IP Address failed, hostname:'{}', message:{}".format(
                    self.address_info.parameter, e
                )
            )
            return

        for item in data:
            if (
                item[0] == socket.AF_INET
                and item[1] == socket.SOCK_STREAM
                and self.address_info.ipv4
            ):
                ip_address = item[4][0]
                if re.match(self.address_info.ipv4_match_rule, ip_address) is None:
                    continue

                self.ipv4_address = ip_address

            elif (
                item[0] == socket.AF_INET6
                and item[1] == socket.SOCK_STREAM
                and self.address_info.ipv6
            ):
                ip_address = item[4][0]
                if re.match(self.address_info.ipv6_match_rule, ip_address) is None:
                    continue

                self.ipv6_address = ip_address
