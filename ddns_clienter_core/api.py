from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from ninja import NinjaAPI, Router, ModelSchema
from ninja.orm import create_schema
from ninja.pagination import paginate, PageNumberPagination

from ddns_clienter_core.models import Status, Address, Task, Event
from runtimes.event import EventLevel
from ddns_clienter_core.runtimes.check_and_update import check_and_update

AddressSchema = create_schema(Address, exclude=[])
TaskSchema = create_schema(Task, exclude=["provider_token"])
StatusSchema = create_schema(Status, exclude=[])


class EventSchema(ModelSchema):
    level: EventLevel

    class Config:
        model = Event
        model_fields = ["id", "level", "message", "time"]


def auth_local_host(request):
    if request.META["REMOTE_ADDR"] == "127.0.0.1":
        return True


api_public = Router(tags=["Public"])


@api_public.get("/addresses", response=list[AddressSchema])
def list_addresses(request):
    addresses = (
        Address.objects.filter(
            time__gt=(timezone.now() - timedelta(minutes=settings.CHECK_INTERVALS * 3))
        )
        .order_by("name")
        .all()
    )
    return addresses


@api_public.get("/addresses/{address_id}", response=AddressSchema)
def get_address(request, address_id: int):
    address = get_object_or_404(AddressSchema, id=address_id)
    return address


@api_public.get("/tasks", response=list[TaskSchema])
def list_tasks(request):
    tasks = (
        Task.objects.filter(
            time__gt=(timezone.now() - timedelta(minutes=settings.CHECK_INTERVALS * 3))
        )
        .order_by("name")
        .all()
    )
    return tasks


@api_public.get("/status", response=list[StatusSchema])
def list_status(request):
    status = Status.objects.order_by("key").all()
    return status


def _get_pagination_range(page: int) -> [int, int]:
    return [(page - 1) * 50, page * 50]


@api_public.get("/events", response=list[EventSchema])
@paginate(PageNumberPagination)
def get_events(request, **kwargs):
    page_range = _get_pagination_range(kwargs.get("pagination").page)
    events = Event.objects.order_by("-time")[page_range[0] : page_range[1]]
    return events


api_inside = Router(auth=auth_local_host, tags=["Inside"])


@api_inside.get("/check_and_update")
def api_check_and_update(request):
    check_and_update()
    return


api = NinjaAPI(title="DDNS Clienter API")
api.add_router("", api_public)
api.add_router("", api_inside)
