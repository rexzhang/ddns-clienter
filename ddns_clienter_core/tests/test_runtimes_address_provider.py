import unittest

from ddns_clienter_core.runtimes.config import AddressConfig
from ddns_clienter_core.runtimes.address_providers.abs import AddressProviderException
from ddns_clienter_core.runtimes.address_providers.host_name import (
    AddressProviderHostName,
)


class MyTestCase(unittest.TestCase):
    def test_something(self):
        address_info = AddressConfig(
            name="test",
            ipv4=True,
            ipv6=True,
            provider="hostname",
            parameter="localhost",
        )
        address_provider = AddressProviderHostName(address_info)
        print(address_provider)
        self.assertEqual(address_provider.ipv4_address, "127.0.0.1")

        address_info.parameter = "not-real-device"
        with self.assertRaises(AddressProviderException):
            AddressProviderHostName(address_info)

        # self.assertEqual(True, False)  # add assertion here


if __name__ == "__main__":
    unittest.main()
