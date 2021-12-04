from typing import Optional

from ddns_clienter_core.runtimes import config


class DDNSProviderException(Exception):
    pass


class DDNSProviderConnectException(DDNSProviderException):
    pass


class DDNSProviderAbs:
    update_success: bool
    message: str

    def __init__(
        self,
        config_task: config.ConfigTask,
        ipv4_address: Optional[str],
        ipv6_address: Optional[str],
        real_update: bool,
    ):
        self._config_task = config_task
        self.real_update = real_update

        # check ip address
        if self._config_task.ipv4 and ipv4_address:
            self.ipv4_address = ipv4_address
        else:
            self.ipv4_address = None

        if self._config_task.ipv6 and ipv6_address:
            self.ipv6_address = ipv6_address
        else:
            self.ipv6_address = None

        if self.ipv4_address is None and self.ipv6_address is None:
            raise Exception("both None")

        # update
        self._update_to_provider()

    def _update_to_provider(self):
        raise NotImplemented
