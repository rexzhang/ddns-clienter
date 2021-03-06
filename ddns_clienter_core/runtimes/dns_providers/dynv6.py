from logging import getLogger

import requests
from requests.structures import CaseInsensitiveDict

from ddns_clienter_core.runtimes.config import TaskConfig
from .abs import DDNSProviderAbs, DDNSProviderException

logger = getLogger(__name__)

_update_api_url = "https://dynv6.com/api/update"
_rest_api_url = "https://dynv6.com/api/v2"


def _call_update_api(
    domain: str,
    token: str,
    ipv4_address: str | None,
    ipv6_address: str | None,
    real_update: bool,
) -> (bool, str):
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

    r = requests.get(_update_api_url, params)
    logger.debug("{} {}".format(r.status_code, r.content))

    if r.status_code == 200:
        return True, r.text
    else:
        return False, r.text


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
        self.ipv4_address = ipv4_address
        self.ipv6_address = ipv6_address
        self.real_update = real_update

        self.headers = CaseInsensitiveDict()
        self.headers["Accept"] = "application/json"
        self.headers["Authorization"] = "Bearer {}".format(self._c_task.provider_auth)

    def _call_rest_api_get(
        self,
        url,
    ) -> requests.Response:
        r = requests.get(url, headers=self.headers)
        logger.debug("{} {}".format(r.status_code, r.content))

        if r.status_code != 200:
            raise DDNSProviderException(r)

        return r

    def _call_rest_api_add_record(
        self, host: str, record_type: str, ip_address: str
    ) -> requests.Response:
        j = {"name": host, "type": record_type, "data": ip_address}
        r = requests.post(
            "{}/zones/{}/records".format(_rest_api_url, self.zone_id),
            headers=self.headers,
            json=j,
        )
        logger.debug("{} {}".format(r.status_code, r.content))

        if r.status_code != 200:
            raise DDNSProviderException(r)

        return r

    def _call_rest_api_update_record(
        self, record_id: str, record_type: str, ip_address: str
    ) -> requests.Response:
        j = {"type": record_type, "data": ip_address}
        r = requests.patch(
            "{}/zones/{}/records/{}".format(_rest_api_url, self.zone_id, record_id),
            headers=self.headers,
            json=j,
        )

        logger.debug("{} {}".format(r.status_code, r.content))

        if r.status_code != 200:
            raise DDNSProviderException(r)

        return r

    def process(self) -> (bool, str):
        # https://dynv6.github.io/api-spec

        # get zone id
        r = self._call_rest_api_get("{}/zones".format(_rest_api_url))

        for item in r.json():
            if item.get("name") == self._c_task.domain:
                self.zone_id = item.get("id")
                continue

        if self.zone_id is None:
            raise DDNSProviderException("Can not match zone id:{}".format(r))

        # get record id
        r = self._call_rest_api_get(
            "{}/zones/{}/records".format(_rest_api_url, self.zone_id)
        )

        ipv4_record_id = None
        ipv6_record_id = None
        for item in r.json():
            if item.get("name") != self._c_task.host:
                continue

            record_type = item.get("type")
            if record_type == "A":
                ipv4_record_id = item.get("id")
            elif record_type == "AAAA":
                ipv6_record_id = item.get("id")

        if self.ipv4_address:
            if ipv4_record_id is None:
                # add a new record
                self._call_rest_api_add_record(
                    host=self._c_task.host,
                    record_type="A",
                    ip_address=self.ipv4_address,
                )
            else:
                # update a record
                self._call_rest_api_update_record(
                    record_id=ipv4_record_id,
                    record_type="A",
                    ip_address=self.ipv4_address,
                )

        if self.ipv6_address:
            if ipv6_record_id is None:
                # add a new record
                self._call_rest_api_add_record(
                    host=self._c_task.host,
                    record_type="AAAA",
                    ip_address=self.ipv6_address,
                )
            else:
                # update a record
                self._call_rest_api_update_record(
                    record_id=ipv6_record_id,
                    record_type="AAAA",
                    ip_address=self.ipv6_address,
                )

        if 200 <= r.status_code <= 299:
            update_success = True
        else:
            update_success = False
        return update_success, "{} {}".format(r.status_code, r.text)


class DDNSProviderDynv6(DDNSProviderAbs):
    def _update_to_provider(self):
        if self.task_config.host is None or len(self.task_config.host) == 0:
            logger.debug("update in Dynv6 UPDATE API")
            update_success, update_message = _call_update_api(
                domain=self.task_config.domain,
                token=self.task_config.provider_auth,
                ipv4_address=self.address_info.ipv4_address_str,
                ipv6_address=self.address_info.ipv6_address_str_with_prefix,
                real_update=self.real_update,
            )

        else:
            logger.debug("update in Dynv6 REST API")
            call_rest_api = CallRestApi(
                config_task=self.task_config,
                ipv4_address=self.address_info.ipv4_address_str,
                ipv6_address=self.address_info.ipv6_address_str,  # REST API ??????????????? /xx ?????????????????? prefix
                real_update=self.real_update,
            )

            update_success, update_message = call_rest_api.process()

        self.update_success = update_success
        self.update_message = update_message
