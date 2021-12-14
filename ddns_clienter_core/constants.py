from dataclasses import dataclass

from django.db import models


@dataclass
class AddressInfo:
    ipv4_address: str
    ipv6_address: str
    ipv6_prefix_length: int | None

    @property
    def ipv6_address_with_prefix(self) -> str:
        if self.ipv6_prefix_length is None:
            return self.ipv6_address

        return "{}/{}".format(self.ipv6_address, self.ipv6_prefix_length)


class EventLevel(models.TextChoices):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
