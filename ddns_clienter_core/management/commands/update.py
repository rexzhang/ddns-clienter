from django.core.management.base import BaseCommand, CommandError

from ddns_clienter_core.runtimes.config import Config
from ddns_clienter_core.runtimes.ip_address_detect_providers import detect_ip_address
from ddns_clienter_core.runtimes.dns_providers import update_to_dns_provider


class Command(BaseCommand):
    help = "Update DyneDNS Recode"

    def add_arguments(self, parser):
        parser.add_argument("-c", "--config", type=str, required=True)

    def handle(self, *args, **options):
        config = Config(options["config"])

        # get ip address, update ip address info into config.addresses
        for address_name in config.addresses:
            ipv4_address, ipv6_address = detect_ip_address(
                config.addresses[address_name]
            )
            config.addresses[address_name].ipv4_address = ipv4_address
            config.addresses[address_name].ipv6_address = ipv6_address

        # put A/AAAA record to DNS provider
        for task in config.tasks:
            address_info = config.addresses.get(task.address_name)
            update_to_dns_provider(
                task, address_info.ipv4_address, address_info.ipv6_address
            ),