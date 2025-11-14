from ddns_clienter.core.constants import AddressInfo
from ddns_clienter.core.runtimes import config


def parser_provider_auth(source: str) -> dict:
    data = dict()

    source_data = source.split(",")
    for item in source_data:
        item_data = item.split(":")
        match len(item_data):
            case 1:
                k = "token"
                v = item_data[0]
            case 2:
                k = item_data[0]
                v = item_data[1]
            case _:
                raise

        data.update({k: v})

    return data


class DDNSProviderException(Exception):
    pass


class DDNSProviderConnectException(DDNSProviderException):
    pass


class DDNSProviderAbs:
    name: str | None = None
    provider_name: str
    address_info: AddressInfo
    update_success: bool
    update_message: str

    def __init__(
        self,
        provider_name: str,
        task_config: config.TaskConfig,
        address_info: AddressInfo,
        real_update: bool,
    ):
        if self.name is None:
            raise NotImplementedError("DDNSProviderAbs.name")

        self.provider_name = provider_name
        self.task_config = task_config
        self.real_update = real_update
        self.address_info = address_info

    async def __call__(self, *args, **kwargs) -> tuple[bool, str]:
        await self._update_to_provider()

        return self.update_success, self.update_message

    async def _update_to_provider(self) -> None:
        raise NotImplementedError
