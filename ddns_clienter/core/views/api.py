from django.conf import settings
from django.shortcuts import get_object_or_404
from ninja import ModelSchema, NinjaAPI, Router
from ninja.orm import create_schema
from ninja.pagination import PageNumberPagination, paginate

from ddns_clienter.core.constants import EventLevel
from ddns_clienter.core.models import Address, Event, Status, Task
from ddns_clienter.core.runtimes.persistent_data import (
    get_addresses_values,
    get_tasks_queryset,
)
from ddns_clienter.core.tasks import check_and_update, test_task
from ddns_clienter.ev import EV

AddressSchema = create_schema(Address, exclude=[])
TaskSchema = create_schema(Task, exclude=["provider_auth"])
StatusSchema = create_schema(Status, exclude=[])


class EventSchema(ModelSchema):
    level: EventLevel

    class Meta:
        model = Event
        fields = ["id", "level", "message", "created_time"]


def auth_inside_api(request):
    if request.META["REMOTE_ADDR"] == "127.0.0.1":
        return True

    if EV.PBULIC_INSIDE_API:
        return True

    return False


api_public = Router(tags=["Public"])


@api_public.get("/addresses", response=list[AddressSchema])
def list_addresses(request, debug: bool = False):
    return get_addresses_values(debug=debug)


@api_public.get("/addresses/{name}", response=AddressSchema)
def get_address(request, name: str):
    data = get_object_or_404(Address, name=name)
    return data


@api_public.get("/tasks", response=list[TaskSchema])
def list_tasks(request, debug: bool = False):
    return get_tasks_queryset(debug=debug)


@api_public.get("/tasks/{name}", response=TaskSchema)
def get_task(request, name: str):
    data = get_object_or_404(Task, name=name)
    return data


@api_public.get("/status", response=list[StatusSchema], deprecated=True)
def list_status(request):
    status = Status.objects.order_by("key").all()
    return status


def _get_pagination_range(page: int) -> tuple[int, int]:
    return ((page - 1) * 50, page * 50)


@api_public.get("/events", response=list[EventSchema])
@paginate(PageNumberPagination)
def get_events(request, **kwargs):
    events = Event.objects.order_by("-created_time").all()
    return events


if settings.DEBUG:
    api_inside = Router(tags=["Inside"])
else:
    api_inside = Router(auth=auth_inside_api, tags=["Inside"])


@api_inside.get("/check_and_update")
async def api_check_and_update(request):
    task_result = await check_and_update.aenqueue()
    return f"{task_result.id}:{task_result.status}"


@api_inside.get("/call_test_task")
async def api_call_test_task(request):
    task_result = await test_task.aenqueue()
    return f"{task_result.id}:{task_result.status}"


api = NinjaAPI(title="DDNS Clienter API")
api.add_router("", api_public)
api.add_router("", api_inside)
