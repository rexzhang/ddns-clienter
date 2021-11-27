from ninja import NinjaAPI, Router
from ninja.orm import create_schema

from ddns_clienter_core.models import Status, Address, Domain


StatusSchema = create_schema(Status, exclude=[])
AddressSchema = create_schema(Address, exclude=[])
DomainSchema = create_schema(Domain, exclude=["provider_token"])


def auth_local_host(request):
    if request.META["REMOTE_ADDR"] == "127.0.0.1":
        return True


router_inside = Router(auth=auth_local_host, tags=["Inside API"])


@router_inside.get("/init_db")
def init(request):
    from django.core.management.commands.migrate import Command

    command = Command()
    migrate_options = {
        # BaseCommand
        "verbosity": 0,
        # Command in migrate
        "skip_checks": None,
        "interactive": False,
        "database": "default",
        "run_syncdb": None,
        "app_label": None,
        "check_unapplied": None,
        "plan": None,
        "fake": None,
        "fake_initial": None,
    }
    command.handle(**migrate_options)


router_web_ui = Router(tags=["Web UI"])


@router_web_ui.get("/status", response=list[StatusSchema])
def list_status(request):
    status = Domain.objects.all()
    return status


@router_web_ui.get("/addresses", response=list[AddressSchema])
def list_addresses(request):
    addresses = Domain.objects.all()
    return addresses


@router_web_ui.post("/domains", response=DomainSchema, deprecated=True)
def upset_domain(request, payload: DomainSchema):
    domains = Domain.objects.create(**payload.dict())
    return domains


@router_web_ui.get("/domains", response=list[DomainSchema])
def list_domains(request):
    tasks = Domain.objects.all()
    return tasks


api = NinjaAPI()
api.add_router("", router_inside)
api.add_router("", router_web_ui)
