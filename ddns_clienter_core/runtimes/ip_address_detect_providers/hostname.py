from typing import Optional
import socket

from ddns_clienter_core.runtimes.config import Address


class ExceptionIPAddressDetect(Exception):
    pass


class IPAddressDetectProviderAbc:
    address_info: Address
    ipv4_match_rule: Optional[str] = None
    ipv6_match_rule: Optional[str] = None

    ipv4_address = None
    ipv6_address = None

    def __init__(self, address_info: Address):
        self.address_info = address_info

    @property
    def name(self):
        raise NotImplemented

    def __repr__(self):
        return "{}:{} {}".format(self.name, self.ipv4_address, self.ipv6_address)


class IPAddressDetectProviderHostName(IPAddressDetectProviderAbc):
    @property
    def name(self):
        return "hostname"

    def get_ip_address(self):
        data = socket.getaddrinfo(self.address_info.parameter, 80)
        for item in data:
            if (
                item[0] == socket.AF_INET
                and item[1] == socket.SOCK_STREAM
                and self.address_info.ipv4
            ):
                self.ipv4_address = item[4][0]
            elif (
                item[0] == socket.AF_INET6
                and item[1] == socket.SOCK_STREAM
                and self.address_info.ipv6
            ):
                if item[4][0].startswith("fd"):
                    continue

                self.ipv6_address = item[4][0]
