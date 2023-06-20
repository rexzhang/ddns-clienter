import asyncio
from datetime import timedelta
from logging import getLogger

from django.utils import timezone

from ddns_clienter_core import models
from ddns_clienter_core.constants import AddressInfo
from ddns_clienter_core.runtimes.address_providers import (
    AddressProviderException,
    get_ip_address_from_provider,
)
from ddns_clienter_core.runtimes.config import (
    AddressProviderConfig,
    ConfigException,
    TaskConfig,
    get_config,
)
from ddns_clienter_core.runtimes.dns_providers import (
    DDNSProviderException,
    update_address_to_dns_provider,
)
from ddns_clienter_core.runtimes.event import event
from ddns_clienter_core.runtimes.persistent_data import (
    compare_and_update_config_info_from_dict_to_db,
)

logger = getLogger(__name__)

_check_and_update_running_lock = asyncio.Lock()


def check_and_update_is_running() -> bool:
    return _check_and_update_running_lock.locked()


async def check_and_update(config_file_name: str | None = None) -> str | None:
    if _check_and_update_running_lock.locked():
        return "There are already tasks in progress, please try later"

    async with _check_and_update_running_lock:
        # await _check_an_update(config_file_name, real_update)
        await _check_an_update_v2(config_file_name)

    return None


class AddressProcessor:
    # TODO 并行处理
    def __init__(self, address_provider_configs: list[AddressProviderConfig]):
        self.address_provider_configs = address_provider_configs

    async def __call__(self):
        for address_config in self.address_provider_configs:
            # migrate config and db
            await compare_and_update_config_info_from_dict_to_db(
                config_item_dict=address_config.dict(),
                model=models.Address,
            )

            if not address_config.enable:
                continue

            address_db = await models.Address.objects.filter(
                name=address_config.name
            ).afirst()

            # get IP address
            try:
                newest_address = await get_ip_address_from_provider(address_config)
            except AddressProviderException as e:
                message = f"Address: {e}"
                logger.error(message)
                await event.error(message)
                continue

            now = timezone.now()

            # update IP address to db
            if (
                address_db.ipv4
                and newest_address.ipv4_address is not None
                and newest_address.ipv4_address_str != address_db.ipv4_last_address
            ):
                # update to db
                address_db.ipv4_previous_address = address_db.ipv4_last_address
                address_db.ipv4_last_address = newest_address.ipv4_address_str
                address_db.ipv4_last_change_time = now
                await address_db.asave()

                # send message
                message = "Address: [{}]'s ipv4 changed:{}->{}".format(
                    address_db.name,
                    address_db.ipv4_previous_address,
                    address_db.ipv4_last_address,
                )
                logger.info(message)
                await event.info(message)

            if (
                address_db.ipv6
                and newest_address.ipv6_address is not None
                and newest_address.ipv6_address_str != address_db.ipv6_last_address
            ):
                # update to db
                address_db.ipv6_previous_address = address_db.ipv6_last_address
                address_db.ipv6_last_address = newest_address.ipv6_address_str
                address_db.ipv6_prefix_length = address_config.ipv6_prefix_length
                address_db.ipv6_last_change_time = now
                await address_db.asave()

                # send message
                message = "Address: [{}]'s ipv6 changed:{}->{}/{}".format(
                    address_db.name,
                    address_db.ipv6_previous_address,
                    address_db.ipv6_last_address,
                    address_db.ipv6_prefix_length,
                )
                logger.info(message)
                await event.info(message)

        return self


class UpdateTaskProcessor:
    # TODO 并行处理

    _address_info_cache: dict

    def __init__(self, task_configs: list[TaskConfig]):
        self._address_info_cache = dict()
        self.task_configs = task_configs

    async def __call__(self):
        config = get_config()

        for task_config in self.task_configs:
            # migrate config and db
            await compare_and_update_config_info_from_dict_to_db(
                config_item_dict=task_config.dict(),
                model=models.Task,
            )

            if not task_config.enable:
                continue

            task_db = await models.Task.objects.filter(name=task_config.name).afirst()

            # check ip address
            address_info = await self.get_newest_ip_address(task_config.address_name)
            now = timezone.now()

            need_update = False
            if (
                task_config.ipv4
                and address_info.ipv4_address
                and (
                    address_info.ipv4_address_str != task_db.last_ip_addresses
                    or task_db.last_update_success_time
                    + timedelta(minutes=config.common.force_update_intervals)
                    < now
                )
            ):
                need_update = True

            if (
                task_config.ipv6
                and address_info.ipv6_address
                and (
                    address_info.ipv6_address_str != task_db.last_ip_addresses
                    or task_db.last_update_success_time
                    + timedelta(minutes=config.common.force_update_intervals)
                    < now
                )
            ):
                need_update = True

            if not need_update:
                continue

            # push dns recode to provider
            try:
                success, message = await update_address_to_dns_provider(
                    task_config, address_info
                )

            except DDNSProviderException as e:
                success = False
                message = str(e)

            if success:
                message = f"Task: Update task:[{task_config.name}] finished, {message}"
                logger.info(message)
                await event.info(message)

                new_addresses = ""
                if task_db.ipv4 and address_info.ipv4_address is not None:
                    new_addresses += address_info.ipv4_address_str

                if task_db.ipv6 and address_info.ipv6_address is not None:
                    if len(new_addresses) != 0:
                        new_addresses += ","

                    new_addresses += address_info.ipv6_address_str

                task_db.last_update_time = now
                task_db.last_update_success = True

                task_db.previous_ip_addresses = task_db.last_ip_addresses
                task_db.last_ip_addresses = new_addresses
                task_db.last_update_success_time = now

            else:
                message = f"Task: Update task:[{task_config.name}] failed, {message}"
                logger.error(message)
                await event.error(message)

                task_db.last_update_time = now
                task_db.last_update_success = False

            # update to db
            await task_db.asave()

    async def get_newest_ip_address(self, address_name: str) -> AddressInfo:
        address_info = self._address_info_cache.get(address_name, None)
        if address_info is not None:
            return address_info

        address_db = await models.Address.objects.filter(name=address_name).afirst()
        if address_db is None:
            # TODO logging
            return AddressInfo()

        address_info = AddressInfo(
            address_db.ipv4_last_address,
            address_db.ipv6_last_address,
            address_db.ipv6_prefix_length,
        )
        self._address_info_cache[address_name] = address_info
        return address_info


async def _check_an_update_v2(config_file_name: str):
    try:
        config = get_config(config_file_name)
    except ConfigException as e:
        logger.critical(e)
        return

    await AddressProcessor(config.address)()
    await UpdateTaskProcessor(config.task)()
