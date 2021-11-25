from django.core.management.base import BaseCommand, CommandError

from ddns_clienter_core.runtimes.config import Config
from ddns_clienter_core.runtimes.ip_address_detect_providers import get_ip_address
from ddns_clienter_core.runtimes.dns_providers import update_to_dns_provider

from icecream import ic


class Command(BaseCommand):
    help = "Update DyneDNS Recode"

    def add_arguments(self, parser):
        parser.add_argument("-c", "--config", type=str, required=True)

    def handle(self, *args, **options):
        config = Config(options["config"])
        ic(config)

        # get ip address
        for name in config.address:
            ipv4_address, ipv6_address = get_ip_address(config.address[name])
            config.address[name].ipv4_address = ipv4_address
            config.address[name].ipv6_address = ipv6_address
        ic(config.address)

        # put A/AAAA record to DNS provider
        for task in config.tasks:
            address_info = config.address.get(task.address_info)
            update_to_dns_provider(
                task, address_info.ipv4_address, address_info.ipv6_address
            ),
