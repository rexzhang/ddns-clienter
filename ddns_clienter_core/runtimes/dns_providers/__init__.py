from ddns_clienter_core.constants import AddressInfo
from ddns_clienter_core.runtimes import config
from ddns_clienter_core.runtimes.dns_providers.abs import DDNSProviderException
from ddns_clienter_core.runtimes.dns_providers.dynv6 import (
    DDNSProviderDynv6,
    DDNSProviderDynv6REST,
)
from ddns_clienter_core.runtimes.dns_providers.lexicon import DDNSProviderLexicon

__all__ = ["DDNSProviderException", "update_address_to_dns_provider"]


_dns_provider_class_mapper = {
    provider_class.name: provider_class
    for provider_class in [
        DDNSProviderDynv6,
        DDNSProviderDynv6REST,
        DDNSProviderLexicon,
    ]
}


async def update_address_to_dns_provider(
    task_config: config.TaskConfig,
    address_info: AddressInfo | None,
    real_update: bool = True,
) -> tuple[bool, str]:
    provider_name = task_config.provider_name.split(".", maxsplit=1)
    provider_name_main = provider_name[0]
    try:
        provider_name_sub = provider_name[1]
    except IndexError:
        provider_name_sub = ""

    provider_class = _dns_provider_class_mapper.get(provider_name_main)
    if provider_class is None:
        raise DDNSProviderException(
            f"Can not match DNS Provider:[{task_config.provider_name}]"
        )

    return await provider_class(
        provider_name_sub, task_config, address_info, real_update
    )()
