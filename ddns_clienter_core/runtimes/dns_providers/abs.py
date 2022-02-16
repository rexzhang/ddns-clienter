from ddns_clienter_core.constants import AddressInfo
from ddns_clienter_core.runtimes import config


class DDNSProviderException(Exception):
    pass


class DDNSProviderConnectException(DDNSProviderException):
    pass


class DDNSProviderAbs:
    address_info: AddressInfo
    update_success: bool
    update_message: str

    def __init__(
        self,
        task_config: config.TaskConfig,
        address_info: AddressInfo,
        real_update: bool,
    ):
        self.task_config = task_config
        self.real_update = real_update
        self.address_info = address_info

        # update
        self._update_to_provider()

    def _update_to_provider(self):
        raise NotImplemented
