import unittest
from pathlib import Path

from ddns_clienter_core.runtimes.config import get_config

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class MyTestCase(unittest.TestCase):
    def test_something(self):
        config = get_config(
            BASE_DIR.joinpath("examples").joinpath("ddns-clienter.toml").as_posix()
        )
        print(config.address_dict)
        self.assertEqual(config.address_dict.get("from_hostname").name, "from_hostname")
        self.assertEqual(
            config.address_dict.get("from_hostname").provider_name, "hostname"
        )
        self.assertEqual(config.address_dict.get("from_hostname").ipv6, True)

        self.assertEqual(config.task_dict.get("ipv6_to_dynv6").name, "ipv6_to_dynv6")
        self.assertEqual(
            config.task_dict.get("ipv6_to_dynv6").address_name, "from_hostname"
        )
        self.assertEqual(config.task_dict.get("ipv6_to_dynv6").ipv6, True)
        self.assertEqual(config.task_dict.get("ipv6_to_dynv6").provider_name, "dynv6")


if __name__ == "__main__":
    unittest.main()
