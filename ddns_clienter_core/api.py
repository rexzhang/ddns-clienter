from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Router, ModelSchema
from ninja.orm import create_schema

from ddns_clienter_core.models import Status, Address, Domain, Event, EventLevel
from ddns_clienter_core.runtimes.event import send_event

StatusSchema = create_schema(Status, exclude=["id"])
AddressSchema = create_schema(Address, exclude=["id"])
DomainSchema = create_schema(Domain, exclude=["id", "provider_token"])
EventSchemaRetrieve = create_schema(Event, exclude=["id"])


class EventCreate(ModelSchema):
    level: EventLevel

    class Config:
        model = Event
        model_exclude = ["id", "time"]


def auth_local_host(request):
    if request.META["REMOTE_ADDR"] == "127.0.0.1":
        return True


api_public = Router(tags=["Public"])


@api_public.get("/events", response=list[EventSchemaRetrieve])
def get_events(request):
    events = Event.objects.order_by("-time").all()
    return events


@api_public.get("/status", response=list[StatusSchema])
def list_status(request):
    status = Domain.objects.all()
    return status


@api_public.get("/addresses", response=list[AddressSchema])
def list_addresses(request):
    addresses = Address.objects.order_by("name").all()
    return addresses


@api_public.get("/addresses/{address_id}", response=AddressSchema)
def get_address(request, address_id: int):
    address = get_object_or_404(AddressSchema, id=address_id)
    return address


@api_public.get("/domains", response=list[DomainSchema])
def list_domains(request):
    domains = Domain.objects.all()
    return domains


api_inside = Router(auth=auth_local_host, tags=["Inside"])


@api_inside.post("/events/create")
def create_event(request, payload: EventCreate):
    # 接受内部提交，接受提交后 console 输出，并且到数据库，可以 api 获取
    event = Event.objects.create(**payload.dict())
    return {"id": event.id}


api = NinjaAPI(title="DDNS Clienter API")
api.add_router("", api_public)
api.add_router("", api_inside)
