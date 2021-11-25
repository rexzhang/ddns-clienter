import unittest

from ddns_clienter_core.runtimes.config import Address
from ddns_clienter_core.runtimes.ip_address_detect_providers.hostname import (
    IPAddressDetectProviderHostName,
    ExceptionIPAddressDetect,
)


class MyTestCase(unittest.TestCase):
    def test_something(self):
        address_info = Address(name="test", provider="hostname")
        detect = IPAddressDetectProviderHostName(address_info)
        detect._detect_ip_address()
        self.assertEqual(detect.ipv4_address, "127.0.0.1")
        # self.assertRaises(
        #     ExceptionIPAddressDetect, detect.get_ip_address("not-real-device")
        # )

        # self.assertEqual(True, False)  # add assertion here


if __name__ == "__main__":
    unittest.main()
