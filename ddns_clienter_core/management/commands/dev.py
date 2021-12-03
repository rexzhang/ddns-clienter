from django.core.management.base import BaseCommand, CommandError

from ddns_clienter_core.runtimes.check_and_update import check_and_update


class Command(BaseCommand):
    help = "dev"

    def add_arguments(self, parser):
        parser.add_argument("-c", "--config", type=str, required=True)

    def handle(self, *args, **options):
        check_and_update(options["config"], real_push=False)
