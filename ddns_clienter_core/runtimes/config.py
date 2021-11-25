from typing import Optional
from dataclasses import dataclass

import toml


@dataclass
class Address:
    name: str
    provider: str
    parameter: str = ""  # for DNS provider

    ipv4: bool = True
    ipv6: bool = True
    ipv4_match_rule: str = ""
    ipv6_match_rule: str = ""

    # update in ip_address_detect_providers
    ipv4_address: Optional[str] = None
    ipv6_address: Optional[str] = None


@dataclass
class Task:
    name: str

    dns_provider: str
    dns_token: str

    domain: str
    host: str

    address_name: str
    ipv4: bool = True
    ipv6: bool = True


class Config:
    addresses = dict()
    tasks = list()

    def __init__(self, file_name: str):
        self._file_name = file_name
        self.load_from_file()

    def load_from_file(self):
        obj = toml.load(self._file_name)
        addresses_obj: dict = obj.get("addresses")
        tasks_obj: dict = obj.get("tasks")
        if addresses_obj is None or tasks_obj is None:
            raise

        for name, data in addresses_obj.items():
            address_info = Address(name=name, **data)
            if not address_info.ipv4 and not address_info.ipv6:
                raise Exception("ipv4 ipv6 both disable")

            self.addresses.update({name: address_info})

        for name, data in tasks_obj.items():
            task = Task(name=name, **data)
            if not task.ipv4 and not task.ipv6:
                raise Exception("ipv4 ipv6 both disable")

            self.tasks.append(task)
