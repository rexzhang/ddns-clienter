from django.core.management.base import BaseCommand, CommandError

from ddns_clienter_core.runtimes.check_and_update import check_and_update


class Command(BaseCommand):
    help = "Check the IP Address and update it to DDNS provider if there is a change. for CLI"

    def add_arguments(self, parser):
        parser.add_argument("-C", "--config", type=str, required=False)
        parser.add_argument("--real-update", action="store_true")

    def handle(self, *args, **options):
        check_and_update(
            config_file_name=options["config"], real_update=options["real_update"]
        )
