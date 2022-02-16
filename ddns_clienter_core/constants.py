from ipaddress import IPv4Address, IPv6Address

from django.db import models


class AddressInfo:
    ipv4_address: IPv4Address | None = None
    ipv6_address: IPv6Address | None = None
    ipv6_prefix_length: int | None = None

    @property
    def ipv4_address_str(self) -> str | None:
        if self.ipv4_address is None:
            return None

        return self.ipv4_address.__str__()

    @property
    def ipv6_address_str(self) -> str | None:
        if self.ipv6_address is None:
            return None

        return self.ipv6_address.__str__()

    @property
    def ipv6_address_str_with_prefix(self) -> str | None:
        if self.ipv6_address is None:
            return None

        if self.ipv6_prefix_length is None:
            return self.ipv6_address.__str__()

        return "{}/{}".format(self.ipv6_address.__str__(), self.ipv6_prefix_length)

    def __init__(
        self,
        ipv4_address: str | None = None,
        ipv6_address: str | None = None,
        ipv6_prefix_length: int | None = None,
    ):
        if ipv4_address:
            self.ipv4_address = IPv4Address(ipv4_address)
        if ipv6_address:
            self.ipv6_address = IPv6Address(ipv6_address)
        if ipv6_prefix_length:
            self.ipv6_prefix_length = ipv6_prefix_length


class EventLevel(models.TextChoices):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
