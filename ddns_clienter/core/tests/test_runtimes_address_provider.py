from ipaddress import IPv4Address, IPv6Address

import pytest

from ddns_clienter.core.runtimes.address_providers.abs import AddressProviderException
from ddns_clienter.core.runtimes.address_providers.host_name import (
    AddressProviderHostName,
)
from ddns_clienter.core.runtimes.address_providers.http_get import pick_out_ip_address
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
