from django.core.management.base import BaseCommand, CommandError
from icecream import ic

from ddns_clienter_core.runtimes.config import Config
from ddns_clienter_core.runtimes.ip_address_detect_providers import detect_ip_address


class Command(BaseCommand):
    help = "Update DyneDNS Recode"

    def add_arguments(self, parser):
        parser.add_argument("-c", "--config", type=str, required=True)

    def handle(self, *args, **options):
        config = Config(options["config"])
        # ic(config.addresses)

        # get ip address, update ip address info into config.addresses
        for address_name in config.addresses:
            ipv4_address, ipv6_address = detect_ip_address(
                config.addresses[address_name]
            )
            config.addresses[address_name].ipv4_address = ipv4_address
            config.addresses[address_name].ipv6_address = ipv6_address

        ic(config.addresses)
