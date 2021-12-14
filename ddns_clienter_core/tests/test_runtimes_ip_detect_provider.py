import unittest

from ddns_clienter_core.runtimes.config import AddressConfig
from ddns_clienter_core.runtimes.ip_address_detect_providers.hostname import (
    DetectAddressProviderHostName,
)
from runtimes.ip_address_detect_providers.abs import ExceptionIPAddressDetect


class MyTestCase(unittest.TestCase):
    def test_something(self):
        address_info = AddressConfig(name="test", provider="hostname")
        detect = DetectAddressProviderHostName(address_info)
        detect._detect_ip_address()
        self.assertEqual(detect.ipv4_last_address, "127.0.0.1")
        # self.assertRaises(
        #     ExceptionIPAddressDetect, detect.get_ip_address("not-real-device")
        # )

        # self.assertEqual(True, False)  # add assertion here


if __name__ == "__main__":
    unittest.main()
