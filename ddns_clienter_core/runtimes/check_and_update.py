import dataclasses
from datetime import timedelta
from logging import getLogger

from asgiref.sync import sync_to_async
from django.utils import timezone

from ddns_clienter_core import models
from ddns_clienter_core.constants import AddressInfo, EventLevel
from ddns_clienter_core.runtimes.address_providers import (
    AddressProviderException,
    get_ip_address_from_provider,
)
from ddns_clienter_core.runtimes.config import (
    AddressProviderConfig,
    Config,
    TaskConfig,
    get_config,
)
from ddns_clienter_core.runtimes.dns_providers import (
    DDNSProviderException,
    update_address_to_dns_provider,
)
from ddns_clienter_core.runtimes.event import send_event
from ddns_clienter_core.runtimes.persistent_data import (
    compare_and_update_config_info_from_dict_to_db,
)

logger = getLogger(__name__)


@dataclasses.dataclass
class AddressDataItem:
    config: AddressProviderConfig
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


class AddressHub:
    # 导入 Address Config+DB 信息
    # 计算获取 需要获取的 addresses 清单，交给 address_provider 去并行处理
    # 等待并导入所有并行处理结果
    # 获得已经改变的 changed_address_names

    _address_provider_config_mapper: dict[str, AddressProviderConfig]
    _data: dict[str, AddressDataItem]
    _changed_names: set[str]

    def __init__(self, address_provider_config: dict[str, AddressProviderConfig]):
        self._address_provider_config_mapper = address_provider_config

    async def __call__(self, *args, **kwargs):
        self._data = dict()

        for address_provider in self._address_provider_config_mapper.values():
            config_changed = await sync_to_async(
                compare_and_update_config_info_from_dict_to_db
            )(
                config_item_dict=dataclasses.asdict(address_provider),
                model=models.Address,
            )

            address_db = await models.Address.objects.filter(
                name=address_provider.name
            ).afirst()
            address_info = AddressInfo(
                address_db.ipv4_last_address,
                address_db.ipv6_last_address,
            )

            self._data.update(
                {
                    address_provider.name: AddressDataItem(
                        address_provider, config_changed, False, False, address_info
                    )
                }
            )

        return self

    @property
    def to_be_update_addresses(self) -> list[AddressProviderConfig]:
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

    def __init__(self, tasks_c: dict[str, TaskConfig]):
        self._data = dict()
        self._config_tasks = tasks_c

    async def __call__(self, *args, **kwargs):
        for task_config_item in self._config_tasks.values():
            if not task_config_item.enable:
                continue

            config_changed = await sync_to_async(
                compare_and_update_config_info_from_dict_to_db
            )(
                config_item_dict=dataclasses.asdict(task_config_item),
                model=models.Task,
            )

            task_db = await models.Task.objects.filter(
                name=task_config_item.name
            ).afirst()

            self._data.update(
                {
                    task_config_item.name: TaskDataItem(
                        task_config_item,
                        config_changed,
                        task_db.last_update_success,
                        False,
                    )
                }
            )
        return self

    async def to_be_update_tasks(self, config: Config) -> list[TaskDataItem]:
        now = timezone.now()
        data = list()
        for item in self._data.values():
            task_db = await models.Task.objects.filter(name=item.config.name).afirst()

            if task_db.last_update_success_time is None or (
                task_db.last_update_success_time
                + timedelta(minutes=config.common.force_update_intervals)
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
    config = get_config(config_file_name)

    # import address data from config and db
    ah = await AddressHub(config.addresses)()

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
    th = await TaskHub(config.tasks)()

    # update to DNS provider
    for task in await th.to_be_update_tasks(config):
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
