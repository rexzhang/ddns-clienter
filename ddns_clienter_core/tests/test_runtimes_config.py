import unittest
from pathlib import Path

from ddns_clienter_core.runtimes.config import Config

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class MyTestCase(unittest.TestCase):
    def test_something(self):
        config = Config(BASE_DIR.joinpath("config.toml").as_posix())
        self.assertEqual(config.address.get("lan_device_01").provider, "hostname")
        self.assertEqual(config.address.get("gateway_ipv4").ipv6, False)


if __name__ == "__main__":
    unittest.main()
