from logging import getLogger
from urllib.parse import urlparse

import httpx

from ddns_clienter.core.runtimes.address_providers.abs import (
    AddressProviderAbs,
    AddressProviderException,
)

logger = getLogger(__name__)

"""
https://openwrt.org/docs/techref/ubus#access_to_ubus_over_http
"""


def _parser_parameter(parameter: str):
    data = urlparse(parameter)
    if (
        data.scheme is None
        or data.username is None
        or data.password is None
        or data.hostname is None
    ):
        raise AddressProviderException(
            "Address Provider parameter is invalid, please check your config. example: http://username:password@hostname/ubus"
        )

    return data.scheme, data.username, data.password, data.hostname


class AddressProviderOpenwrtUbusRpc(AddressProviderAbs):
    name = "openwrt_ubus_rpc"

    async def _get_address_from_openwrt(self) -> tuple[str | None, str | None]:
        login_response = None
        ubus_response = None

        try:
            ubus_url = f"http://{self.hostname}/ubus"

            # 获取会话token
            login_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "call",
                "params": [
                    "00000000000000000000000000000000",
                    "session",
                    "login",
                    {"username": self.username, "password": self.password},
                ],
            }

            login_response = httpx.post(ubus_url, json=login_payload, verify=False)
            if login_response.status_code != 200:
                raise AddressProviderException("Access openwrt ubus failed.")

            if "access denied" in login_response.text:
                raise AddressProviderException(
                    "Access openwrt ubus failed. please check username/password."
                )

            login_data = login_response.json()
            ubus_rpc_session = login_data["result"][1]["ubus_rpc_session"]

            # 获取网络信息
            ubus_payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "call",
                "params": [ubus_rpc_session, "network.interface", "dump", {}],
            }

            ubus_response = httpx.post(ubus_url, json=ubus_payload, verify=False)
            if ubus_response.status_code != 200:
                raise AddressProviderException("Access openwrt ubus failed(2).")

            ubus_data = ubus_response.json()
            interfaces = ubus_data["result"][1]["interface"]
            ipv4, ipv6 = None, None
            for interface in interfaces:
                if interface["interface"] == "wan":
                    ipv4 = interface["ipv4-address"][0].get("address")

                elif interface["interface"] == "wan_6":
                    ipv6 = interface["ipv6-address"][0].get("address")
                    # TODO: 返回 mask 值
                    # ipv6_mask = interface["ipv6-address"][0].get("mask")

        except (KeyError, AddressProviderException) as e:
            if login_response is not None:
                logger.info(f"openwrt ubus response: {login_response.text}")
            if ubus_response is not None:
                logger.info(f"openwrt ubus response: {ubus_response.text}")

            raise AddressProviderException(
                f"Detect IP Address failed, provider:[{self.name}]; message:{e}; detail info please check logging"
            )

        logger.debug(f"openwrt ubus response: {ubus_response.text}")
        logger.info(f"Detect IP Address IPv4{ipv4}, IPv6{ipv6} from openwrt ubus")
        return ipv4, ipv6

    async def _get_address(
        self, ipv4: bool, ipv6: bool, parameter: str
    ) -> tuple[list[str], list[str]]:
        self.parameter = parameter

        self.scheme, self.username, self.password, self.hostname = _parser_parameter(
            parameter
        )

        ipv4_address, ip6v_address = await self._get_address_from_openwrt()
        if ipv4 and ipv4_address is not None:
            ipv4_addresses = [ipv4_address]
        else:
            ipv4_addresses = []

        if ipv6 and ip6v_address is not None:
            ipv6_addresses = [ip6v_address]
        else:
            ipv6_addresses = []

        return ipv4_addresses, ipv6_addresses
