from dataclasses import dataclass

import toml


@dataclass
class Address:
    name: str
    provider: str
    parameter: str = ""
    ipv4: bool = True
    ipv6: bool = True
    # ipv4_address: str = None
    # ipv6_address: str = None


@dataclass
class Task:
    name: str
    dns_provider: str
    dns_token: str

    domain: str
    host: str

    address: str
    ipv4: bool = False
    ipv6: bool = False


class Config:
    address = dict()
    tasks = list()

    def __init__(self, file_name: str):
        self._file_name = file_name
        self.load()

    def load(self):
        obj = toml.load(self._file_name)
        address_info_obj: dict = obj.get("address")
        tasks_obj: dict = obj.get("tasks")
        if address_info_obj is None or tasks_obj is None:
            raise

        for name, data in address_info_obj.items():
            ip_address = Address(name=name, **data)
            self.address.update({name: ip_address})

        for name, data in tasks_obj.items():
            task = Task(name=name, **data)
            self.tasks.append(task)
