import json
from ipaddress import IPv4Address, IPv6Address

import httpx2
import pytest

from ddns_clienter.core.runtimes.address_providers.abs import AddressProviderException
from ddns_clienter.core.runtimes.address_providers.host_name import (
    AddressProviderHostName,
)
from ddns_clienter.core.runtimes.address_providers.http_get import pick_out_ip_address
from ddns_clienter.core.runtimes.address_providers.openwrt_ubus import (
    AddressProviderOpenwrtUbusRpc,
)
from ddns_clienter.core.runtimes.config import AddressProviderConfig


@pytest.mark.asyncio
async def test_something():
    address_provider_config = AddressProviderConfig(
        name="test",
        ipv4=True,
        ipv6=True,
        allow_loopback=True,
        provider_name="hostname",
        provider_parameter="localhost",
    )
    ip_address = await AddressProviderHostName()(address_provider_config)
    assert ip_address.ipv4_address == IPv4Address("127.0.0.1")
    assert ip_address.ipv6_address == IPv6Address("::1")

    address_provider_config.provider_parameter = "not-real-device"
    with pytest.raises(AddressProviderException):
        await AddressProviderHostName()(address_provider_config)


def test_address_provider_cip():
    data = """<div><pre>
    URL	: http://www.cip.cc/111.222.333.444
    </pre>
    </div>
    <div class="i-don-t-like-you">
    </div>"""

    assert pick_out_ip_address(4, data) == "111.222.333.444"


@pytest.mark.asyncio
async def test_address_provider_openwrt_ubus(monkeypatch):
    def handler(request: httpx2.Request) -> httpx2.Response:
        payload = json.loads(request.content)
        if payload["id"] == 1:
            return httpx2.Response(
                200,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": [0, {"ubus_rpc_session": "1234567890abcdef"}],
                },
            )

        return httpx2.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "result": [
                    0,
                    {
                        "interface": [
                            {
                                "interface": "wan",
                                "ipv4-address": [{"address": "1.2.3.4"}],
                            },
                            {
                                "interface": "wan_6",
                                "ipv6-address": [{"address": "2606:4700:4700::1111"}],
                            },
                        ]
                    },
                ],
            },
        )

    real_async_client = httpx2.AsyncClient

    def factory(*args, **kwargs):
        kwargs["transport"] = httpx2.MockTransport(handler)
        return real_async_client(*args, **kwargs)

    monkeypatch.setattr(httpx2, "AsyncClient", factory)

    address_provider_config = AddressProviderConfig(
        name="test",
        ipv4=True,
        ipv6=True,
        allow_loopback=True,
        provider_name="openwrt_ubus_rpc",
        provider_parameter="http://user:pass@192.168.1.1/ubus",
    )
    ip_address = await AddressProviderOpenwrtUbusRpc()(address_provider_config)
    assert ip_address.ipv4_address == IPv4Address("1.2.3.4")
    assert ip_address.ipv6_address == IPv6Address("2606:4700:4700::1111")
