from ddns_clienter_core.constants import AddressInfo
from ddns_clienter_core.runtimes import config
from ddns_clienter_core.runtimes.dns_providers.abs import DDNSProviderException
from ddns_clienter_core.runtimes.dns_providers.dynv6 import DDNSProviderDynv6

__all__ = ["DDNSProviderException", "update_address_to_dns_provider"]


def update_address_to_dns_provider(
    config_task: config.TaskConfig,
    address_info: AddressInfo | None,
    real_update: bool = True,
):
    if config_task.provider == "dynv6":
        provider_class = DDNSProviderDynv6

    else:
        raise DDNSProviderException("Can not match DNS provider")

    provider = provider_class(config_task, address_info, real_update)
    return provider.update_success
