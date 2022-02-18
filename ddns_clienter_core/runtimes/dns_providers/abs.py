from ddns_clienter_core.constants import AddressInfo
from ddns_clienter_core.runtimes import config


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
    provider_name = None
    provider_name_sub = None
    address_info: AddressInfo
    update_success: bool
    update_message: str

    def __init__(
        self,
        provider_name: list[str],
        task_config: config.TaskConfig,
        address_info: AddressInfo,
        real_update: bool,
    ):
        match len(provider_name):
            case 1:
                self.provider_name = provider_name[0]
            case 2:
                self.provider_name = provider_name[0]
                self.provider_name_sub = provider_name[1]
            case _:
                raise

        self.task_config = task_config
        self.real_update = real_update
        self.address_info = address_info

        # update
        self._update_to_provider()

    def _update_to_provider(self):
        raise NotImplemented
