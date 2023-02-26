import dataclasses
from datetime import timedelta
from logging import getLogger

from asgiref.sync import sync_to_async
from django.conf import settings
from django.forms.models import model_to_dict
from django.utils import timezone

from ddns_clienter_core import models
from ddns_clienter_core.constants import AddressInfo, EventLevel
from ddns_clienter_core.runtimes.address_providers import (
    AddressProviderException,
    get_ip_address_from_provider,
)
from ddns_clienter_core.runtimes.config import AddressConfig, TaskConfig
from ddns_clienter_core.runtimes.dns_providers import (
    DDNSProviderException,
    update_address_to_dns_provider,
)
from ddns_clienter_core.runtimes.event import send_event

logger = getLogger(__name__)


@dataclasses.dataclass
class AddressDataItem:
    config: AddressConfig
    config_changed: bool

    ipv4_changed: bool
    ipv6_changed: bool
    newest_address: AddressInfo

    @property
    def there_ars_changes(self) -> bool:
        """config changed or address changed"""
        if self.config_changed or self.ipv4_changed or self.ipv6_changed:
            return True

        return False


class CannotMatchAddressException(Exception):
    pass


def compare_and_update_from_dataclass_to_db(dc_obj, db_obj) -> bool:
    changed = False
    data = model_to_dict(db_obj)
    for k, v in dataclasses.asdict(dc_obj).items():
        if data.get(k) != v:
            changed = True
            db_obj.__setattr__(k, v)

    return changed


class AddressHub:
    # 导入 Address Config+DB 信息
    # 计算获取 需要获取的 addresses 清单，交给 address_provider 去并行处理
    # 等待并导入所有并行处理结果
    # 获得已经改变的 changed_address_names

    _address_configs: dict[str, AddressConfig]
    _data: dict[str, AddressDataItem]
    _changed_names: set[str]

    @staticmethod
    async def _compare_and_update_from_config_to_db(
        address_c: AddressConfig,
    ) -> (bool, AddressInfo):
        address_db = await models.Address.objects.filter(name=address_c.name).afirst()
        if address_db is None:
            address_db = models.Address(**dataclasses.asdict(address_c))
            await sync_to_async(address_db.save)()
            logger.info(f"Cannot found address:{address_c.name} from db, create it.")
            return True, AddressInfo()

        changed = compare_and_update_from_dataclass_to_db(address_c, address_db)
        if changed:
            await sync_to_async(address_db.save)()
            logger.info(
                "The address[{}]'s config has changed, update to db.".format(
                    address_c.name
                )
            )
            return (
                True,
                AddressInfo(
                    address_db.ipv4_last_address,
                    address_db.ipv6_last_address,
                ),
            )

        logger.debug(f"The address[{address_c.name}] no change in config")
        return (
            False,
            AddressInfo(
                address_db.ipv4_last_address,
                address_db.ipv6_last_address,
            ),
        )

    def __init__(self, address_configs: dict[str, AddressConfig]):
        self._address_configs = address_configs

    async def __call__(self, *args, **kwargs):
        self._data = dict()

        for address_c in self._address_configs.values():
            (
                config_changed,
                address_info,
            ) = await self._compare_and_update_from_config_to_db(address_c)

            self._data.update(
                {
                    address_c.name: AddressDataItem(
                        address_c, config_changed, False, False, address_info
                    )
                }
            )

        return self

    @property
    def to_be_update_addresses(self) -> list[AddressConfig]:
        data = list()
        for item in self._data.values():
            data.append(item.config)

        logger.debug(f"To be update addresses:{data}")
        return data

    async def update_ip_address(
        self,
        name: str,
        newest_address: AddressInfo,
    ):
        address_data = self._data.get(name)
        now = timezone.now()
        address_db = await models.Address.objects.filter(name=name).afirst()

        if (
            newest_address.ipv4_address is not None
            and newest_address.ipv4_address != address_data.newest_address.ipv4_address
        ):
            address_data.ipv4_changed = True
            address_data.newest_address.ipv4_address = newest_address.ipv4_address

            address_db.ipv4_previous_address = address_db.ipv4_last_address
            address_db.ipv4_last_address = newest_address.ipv4_address
            address_db.ipv4_last_change_time = now

            message = "{}'s ipv4 changed:{}->{}".format(
                name,
                address_db.ipv4_previous_address,
                address_db.ipv4_last_address,
            )
            logger.info(message)
            await send_event(message)

        if newest_address.ipv6_address is not None and (
            newest_address.ipv6_address != address_data.newest_address.ipv6_address
        ):
            message = "{}'s ipv6 changed:{}->{}/{}".format(
                name,
                address_db.ipv6_last_address,  # last
                newest_address.ipv6_address,  # new
                address_data.config.ipv6_prefix_length,
            )
            logger.info(message)
            await send_event(message)

            # update to self._data
            address_data.ipv6_changed = True
            address_data.newest_address.ipv6_address = newest_address.ipv6_address
            address_data.newest_address.ipv6_prefix_length = (
                address_data.config.ipv6_prefix_length
            )

            # update to db
            address_db.ipv6_previous_address = address_db.ipv6_last_address
            address_db.ipv6_last_address = newest_address.ipv6_address
            address_db.ipv6_prefix_length = address_data.config.ipv6_prefix_length
            address_db.ipv6_last_change_time = now

        await sync_to_async(address_db.save)()

    def get_address_info_if_changed(
        self, name: str, force_update: bool  # TODO
    ) -> AddressInfo | None:
        address_data = self._data.get(name)
        if address_data is None:
            raise CannotMatchAddressException()

        if force_update or address_data.there_ars_changes:
            return address_data.newest_address

        return None


@dataclasses.dataclass
class TaskDataItem:
    config: TaskConfig
    _config_changed: bool
    _last_update_success: bool
    _force_update_intervals_timeout: bool

    @property
    def force_update(self) -> bool:
        return (
            self._config_changed
            or not self._last_update_success
            or self._force_update_intervals_timeout
        )


class TaskHub:
    # 根据 changed_address_names 获取更新信息清单，交给 dns_provider 去并行处理
    # 等待并导入所有并行处理结果
    # 将更新任务结果存储到 DB

    _config_tasks: dict[str, TaskConfig]
    _data: dict[str, TaskDataItem]

    @staticmethod
    async def _compare_and_update_from_config_to_db(task_c: TaskConfig) -> (bool, bool):
        task_db = await models.Task.objects.filter(name=task_c.name).afirst()
        if task_db is None:
            task_db = models.Task(**dataclasses.asdict(task_c))
            await sync_to_async(task_db.save)()
            logger.info(f"Cannot found task:{task_c.name} from db, create it in db.")

            return True, False

        changed = compare_and_update_from_dataclass_to_db(task_c, task_db)
        if changed:
            await sync_to_async(task_db.save)()
            logger.info(f"The task[{task_c.name}]'s config has changed, update to db.")
            return True, task_db.last_update_success

        logger.debug(f"The task[{task_c.name}] no change in config")
        return False, task_db.last_update_success

    def __init__(self, tasks_c: dict[str, TaskConfig]):
        self._data = dict()
        self._config_tasks = tasks_c

    async def __call__(self, *args, **kwargs):
        for tasks_c in self._config_tasks.values():
            (
                config_changed,
                last_update_success,
            ) = await self._compare_and_update_from_config_to_db(tasks_c)
            self._data.update(
                {
                    tasks_c.name: TaskDataItem(
                        tasks_c,
                        config_changed,
                        last_update_success,
                        False,
                    )
                }
            )
        return self

    async def to_be_update_tasks(self) -> list[TaskDataItem]:
        now = timezone.now()
        data = list()
        for item in self._data.values():
            task_db = await models.Task.objects.filter(name=item.config.name).afirst()

            if task_db.last_update_success_time is None or (
                task_db.last_update_success_time
                + timedelta(minutes=settings.CONFIG.common.force_update_intervals)
                < now
            ):
                # force_update_intervals timeout
                item._force_update_intervals_timeout = True
                data.append(item)
                continue

            # other task
            data.append(item)

        logger.debug(f"To be update tasks:{data}")
        return data

    @staticmethod
    async def set_task_skipped(name: str):
        task_db = await models.Task.objects.filter(name=name).afirst()
        await sync_to_async(task_db.save)()

    @staticmethod
    async def save_update_status_to_db(
        name: str, address_info: AddressInfo, update_success: bool
    ):
        db_task = await models.Task.objects.filter(name=name).afirst()

        now = timezone.now()
        if update_success:
            new_addresses = ""
            if db_task.ipv4 and address_info.ipv4_address is not None:
                new_addresses += address_info.ipv4_address_str

            if db_task.ipv6 and address_info.ipv6_address is not None:
                if len(new_addresses) != 0:
                    new_addresses += ","

                new_addresses += address_info.ipv6_address_str_with_prefix

            db_task.last_update_time = now
            db_task.last_update_success = True

            db_task.previous_ip_addresses = db_task.last_ip_addresses
            db_task.last_ip_addresses = new_addresses
            db_task.last_update_success_time = now

        else:
            db_task.last_update_time = now
            db_task.last_update_success = False

        await sync_to_async(db_task.save)()


async def check_and_update(
    config_file_name: str | None = None, real_update: bool = True
):
    if config_file_name is not None:
        raise "TODO"

    # import address data from config and db
    ah = await AddressHub(settings.CONFIG.addresses)()

    # get ip address, update ip address into hub
    for address_c in ah.to_be_update_addresses:
        try:
            address_info = await get_ip_address_from_provider(address_c)

        except AddressProviderException as e:
            message = str(e)
            logger.error(message)
            await send_event(message, level=EventLevel.ERROR)
            continue

        await ah.update_ip_address(address_c.name, address_info)
        logger.debug(f"address info:{address_c.name}, {address_info}")

    # import address data from config and db
    th = await TaskHub(settings.CONFIG.tasks)()

    # update to DNS provider
    for task in await th.to_be_update_tasks():
        try:
            address_info = ah.get_address_info_if_changed(
                task.config.address_name, task.force_update
            )

        except CannotMatchAddressException:
            message = f"Cannot found address:{task.config.address_name}"
            logger.warning(message)
            await send_event(message, level=EventLevel.WARNING)
            continue

        if address_info is None:
            logger.debug(
                "Skip task:{}, because address have not any change".format(
                    task.config.name
                )
            )

            await th.set_task_skipped(task.config.name)
            continue

        if address_info.ipv4_address is None and address_info.ipv6_address is None:
            message = "{}: ipv4_address and ipv6_address both None".format(
                task.config.address_name
            )
            logger.warning(message)
            await send_event(message, level=EventLevel.WARNING)

            await th.set_task_skipped(task.config.name)
            continue

        # check ip address
        if not task.config.ipv4:
            address_info.ipv4_address = None

        if not task.config.ipv6:
            address_info.ipv6_address = None
            address_info.ipv6_prefix_length = None

        if address_info.ipv4_address is None and address_info.ipv6_address is None:
            message = "Skip task:{}, because address do not need update".format(
                task.config.name
            )
            logger.warning(message)
            await send_event(message, level=EventLevel.WARNING)

            await th.set_task_skipped(task.config.name)
            continue

        try:
            update_success, update_message = await update_address_to_dns_provider(
                task.config, address_info, real_update
            )

        except DDNSProviderException as e:
            message = str(e)
            logger.error(message)
            await send_event(message, level=EventLevel.ERROR)
            continue

        if update_success:
            message = f"update task:{task.config.name} finished"
            logger.info(message)
            await send_event(message)
        else:
            message = f"update task:{task.config.name} failed, {update_message}"
            logger.warning(message)
            await send_event(message, level=EventLevel.WARNING)

        await th.save_update_status_to_db(
            task.config.name, address_info, update_success
        )
