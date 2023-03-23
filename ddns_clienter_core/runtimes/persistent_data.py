import dataclasses
from datetime import timedelta
from logging import getLogger

from asgiref.sync import async_to_sync, sync_to_async
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict
from django.utils import timezone

from ddns_clienter_core.models import Address, Event, Task
from ddns_clienter_core.runtimes.config import get_config
from ddns_clienter_core.runtimes.event import event

logger = getLogger(__name__)


async def compare_and_update_from_dataclass_to_db(dc_obj, db_obj) -> bool:
    changed = False
    data = model_to_dict(db_obj)
    for k, v in dataclasses.asdict(dc_obj).items():
        if data.get(k) != v:
            changed = True
            db_obj.__setattr__(k, v)

    if changed:
        await sync_to_async(db_obj.save)()

    return changed


async def compare_and_update_config_info_from_dict_to_db(
    config_item_dict: dict, model: type[Address] | type[Task]
) -> bool:
    """
    :param config_item_dict: dict
    :param model:
    :return: bool  # config changed/have new item
    """
    config_item_name = config_item_dict.get("name")
    if config_item_name is None:
        raise

    config_item_db = await model.objects.filter(name=config_item_name).afirst()
    if config_item_db is None:
        config_item_db = model(**config_item_dict)
        await sync_to_async(config_item_db.save)()

        message = f"Cannot found config item:{model.__name__}:{config_item_name} from db, create it in db."
        logger.info(message)
        await event.info(message)
        return True

    changed = False
    config_item_db_to_dict = model_to_dict(config_item_db)
    for k, v in config_item_dict.items():
        if config_item_db_to_dict.get(k) != v:
            config_item_db.__setattr__(k, v)
            changed = True

    if changed:
        await sync_to_async(config_item_db.save)()

        message = f"The {model.__name__}:{config_item_name}'s config has changed, update to db."
        logger.info(message)
        await event.info(message)
        return True

    return False


def get_addresses_values(debug: bool = False) -> QuerySet:
    config = get_config()

    for _, address_config_item in config.addresses.items():
        async_to_sync(compare_and_update_config_info_from_dict_to_db)(
            dataclasses.asdict(address_config_item), Address
        )

    if debug:
        queryset = Address.objects.filter(
            time__gt=(timezone.now() - timedelta(weeks=1))
        )
    else:
        queryset = Address.objects.filter(name__in=config.addresses.keys())

    return queryset.order_by("name")


def get_tasks_queryset(debug: bool = False) -> QuerySet:
    config = get_config()

    for _, task_config_item in config.tasks.items():
        async_to_sync(compare_and_update_config_info_from_dict_to_db)(
            dataclasses.asdict(task_config_item), Task
        )

    if debug:
        queryset = Task.objects.filter(time__gt=(timezone.now() - timedelta(weeks=1)))
    else:
        queryset = Task.objects.filter(name__in=config.tasks.keys())

    return queryset.order_by("name")


def get_events_queryset(debug: bool = False) -> QuerySet:
    queryset_init = Event.objects.order_by("-id")

    if debug:
        return queryset_init

    queryset = queryset_init.filter(time__gt=(timezone.now() - timedelta(days=2)))
    if len(queryset) < 10:
        return queryset_init.order_by("-id")[:10]
    else:
        return queryset
