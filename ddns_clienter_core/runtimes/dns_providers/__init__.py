from ddns_clienter_core.runtimes.config import Task
from ddns_clienter_core.runtimes.dns_providers.dynv6 import DNSProviderDynv6


def update_to_dns_provider(task: Task, ipv4_address: str, ipv6_address: str):
    dns_provider = DNSProviderDynv6()
    dns_provider.update(task, ipv4_address, ipv6_address)
