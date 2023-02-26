from ddns_clienter_core.constants import AddressInfo
from ddns_clienter_core.runtimes import config
from ddns_clienter_core.runtimes.dns_providers.abs import DDNSProviderException
from ddns_clienter_core.runtimes.dns_providers.dynv6 import DDNSProviderDynv6
from ddns_clienter_core.runtimes.dns_providers.lexicon import DDNSProviderLexicon

__all__ = ["DDNSProviderException", "update_address_to_dns_provider"]


async def update_address_to_dns_provider(
    task_config: config.TaskConfig,
    address_info: AddressInfo | None,
    real_update: bool = True,
) -> (bool, str):
    provider_name = task_config.provider.split(".")
    match provider_name[0]:
        case "dynv6":
            provider_class = DDNSProviderDynv6
        case "lexicon":
            provider_class = DDNSProviderLexicon
        case _:
            raise DDNSProviderException("Can not match DNS provider")

    provider = await provider_class(
        provider_name, task_config, address_info, real_update
    )()
    return provider.update_success, provider.update_message
