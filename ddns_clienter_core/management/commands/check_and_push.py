from django.core.management.base import BaseCommand, CommandError

from ddns_clienter_core.runtimes.check_and_update import check_and_push


class Command(BaseCommand):
    help = "Check the IP Address and push it to DDNS provider if there is a change"

    def add_arguments(self, parser):
        parser.add_argument("-C", "--config", type=str, required=True)
        parser.add_argument("--send-event", action="store_true")

    def handle(self, *args, **options):
        check_and_push(config_file=options["config"], send_event=options["send_event"])
