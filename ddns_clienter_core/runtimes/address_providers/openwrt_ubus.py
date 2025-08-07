from ddns_clienter_core.runtimes.address_providers.abs import (
    AddressProviderAbs,
    AddressProviderException,
)
from logging import getLogger
import httpx

from urllib.parse import urlparse


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
    name = "openwrt-ubus-rpc"

    async def _get_address_from_openwrt(self) -> tuple[str | None, str | None]:
        try:
            ubus_url = f"http://{self.hostname}/ubus"
            session_payload = {
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
            client = httpx.Client()

            # 获取会话token
            session_response = client.post(ubus_url, json=session_payload)
            if session_response.status_code != 200:
                raise AddressProviderException("Access openwrt ubus failed.")

            if "access denied" in session_response.text:
                raise AddressProviderException(
                    "Access openwrt ubus failed. please check username/password."
                )

            session_data = session_response.json()
            ubus_rpc_session = session_data["result"][1]["ubus_rpc_session"]

            # 获取网络信息
            network_payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "call",
                "params": [ubus_rpc_session, "network.interface.wan", "dump", {}],
            }

            network_response = client.post(ubus_url, json=network_payload)
            if network_response.status_code != 200:
                raise AddressProviderException("Access openwrt ubus failed(2).")

            network_data = network_response.json()
            interfaces = network_data["result"][1]["interface"]
            ipv4, ipv6 = None, None
            for interface in interfaces:
                if interface["interface"] == "wan":
                    ipv4 = interface["ipv4-address"][0].get("address")
                    ipv6 = interface["ipv6-address"][0].get("address")

                    break

        except Exception as e:
            raise AddressProviderException(
                f"Detect IP Address failed, provider:[{self.name}], parameter:{self.parameter}; message:{e}"
            )

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
