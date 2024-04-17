from logging import getLogger

import httpx

from ddns_clienter_core.runtimes.config import TaskConfig

from .abs import DDNSProviderAbs, DDNSProviderException

logger = getLogger(__name__)

_UPDATE_API_URL = "https://dynv6.com/api/update"
_REST_API_URL = "https://dynv6.com/api/v2"


class CallRestApi:
    zone_id: int | None = None

    def __init__(
        self,
        config_task: TaskConfig,
        ipv4_address: str,
        ipv6_address: str,
        real_update: bool,
    ):
        self._c_task = config_task
        self.config_host, self.config_domain = config_task.domain.split(".", maxsplit=1)
        self.ipv4_address = ipv4_address
        self.ipv6_address = ipv6_address
        self.real_update = real_update

        self.headers = httpx.Headers()
        self.headers["Accept"] = "application/json"
        self.headers["Authorization"] = f"Bearer {self._c_task.provider_auth}"

    async def _call_rest_api_get(self, url) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self.headers)
        logger.debug(f"{r.status_code} {r.content}")

        if r.status_code != 200:
            raise DDNSProviderException(r)

        return r

    async def _call_rest_api_add_record(
        self, host: str, record_type: str, ip_address: str
    ) -> httpx.Response:
        j = {"name": host, "type": record_type, "data": ip_address}
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{_REST_API_URL}/zones/{self.zone_id}/records",
                headers=self.headers,
                json=j,
            )
        logger.debug(f"{r.status_code} {r.content}")

        if r.status_code != 200:
            raise DDNSProviderException(r)

        return r

    async def _call_rest_api_update_record(
        self, record_id: str, record_type: str, ip_address: str
    ) -> httpx.Response:
        j = {"type": record_type, "data": ip_address}
        async with httpx.AsyncClient() as client:
            r = await client.patch(
                f"{_REST_API_URL}/zones/{self.zone_id}/records/{record_id}",
                headers=self.headers,
                json=j,
            )

        logger.debug(f"{r.status_code} {r.content}")

        if r.status_code != 200:
            raise DDNSProviderException(r)

        return r

    async def process(self) -> tuple[bool, str]:
        # https://dynv6.github.io/api-spec

        # get zone id
        r = await self._call_rest_api_get(f"{_REST_API_URL}/zones")

        for item in r.json():
            if item.get("name") == self.config_domain:
                self.zone_id = item.get("id")
                continue

        if self.zone_id is None:
            raise DDNSProviderException(f"Can not match zone id:{r}")

        # get record id
        r = await self._call_rest_api_get(
            f"{_REST_API_URL}/zones/{self.zone_id}/records"
        )

        ipv4_record_id = None
        ipv6_record_id = None
        for item in r.json():
            if item.get("name") != self.config_host:
                continue

            record_type = item.get("type")
            if record_type == "A":
                ipv4_record_id = item.get("id")
            elif record_type == "AAAA":
                ipv6_record_id = item.get("id")

        if self.ipv4_address:
            if ipv4_record_id is None:
                # add a new record
                await self._call_rest_api_add_record(
                    host=self.config_host,
                    record_type="A",
                    ip_address=self.ipv4_address,
                )
            else:
                # update a record
                await self._call_rest_api_update_record(
                    record_id=ipv4_record_id,
                    record_type="A",
                    ip_address=self.ipv4_address,
                )

        if self.ipv6_address:
            if ipv6_record_id is None:
                # add a new record
                await self._call_rest_api_add_record(
                    host=self.config_host,
                    record_type="AAAA",
                    ip_address=self.ipv6_address,
                )
            else:
                # update a record
                await self._call_rest_api_update_record(
                    record_id=ipv6_record_id,
                    record_type="AAAA",
                    ip_address=self.ipv6_address,
                )

        if 200 <= r.status_code <= 299:
            update_success = True
        else:
            update_success = False
        return update_success, f"{r.status_code} {r.text}"


class DDNSProviderDynv6(DDNSProviderAbs):
    name = "dynv6"

    async def _update_to_provider(self) -> None:
        logger.debug("update in Dynv6 UPDATE API")
        self.update_success, self.update_message = await self._call_update_api(
            domain=self.task_config.domain,
            token=self.task_config.provider_auth,
            ipv4_address=self.address_info.ipv4_address_str,
            ipv6_address=self.address_info.ipv6_address_str_with_prefix,
            real_update=self.real_update,
        )

    @staticmethod
    async def _call_update_api(
        domain: str,
        token: str,
        ipv4_address: str | None,
        ipv6_address: str | None,
        real_update: bool,
    ) -> tuple[bool, str]:
        # https://dynv6.com/docs/apis
        params = {
            "zone": domain,
            "token": token,
        }
        if ipv4_address:
            params.update({"ipv4": ipv4_address})
        if ipv6_address:
            params.update({"ipv6": ipv6_address})

        logger.debug(params)
        if not real_update:
            return True, ""

        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(_UPDATE_API_URL, params=params)

        except (httpx.HTTPError, httpx.StreamError) as e:
            return False, f"httpx request failed, {str(e)}"

        message = f"code:{r.status_code}, text:{r.text}"
        if 300 > r.status_code >= 200:
            return True, message
        else:
            return False, message


class DDNSProviderDynv6REST(DDNSProviderAbs):
    name = "dynv6.rest"

    async def _update_to_provider(self) -> None:
        logger.debug("update in Dynv6 REST API")
        call_rest_api = CallRestApi(
            config_task=self.task_config,
            ipv4_address=self.address_info.ipv4_address_str,
            ipv6_address=self.address_info.ipv6_address_str,  # REST API 似乎不支持 /xx 这种方式定义 prefix
            real_update=self.real_update,
        )

        self.update_success, self.update_message = await call_rest_api.process()
