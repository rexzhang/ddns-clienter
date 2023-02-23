import unittest

from ddns_clienter_core.runtimes.dns_providers.abs import parser_provider_auth


class MyTestCase(unittest.TestCase):
    def test_something(self):
        token_key = "token"
        token_value = "this-is-token-for-this-zone"

        auth = parser_provider_auth(f"{token_value}")
        self.assertEqual(auth.get(token_key), token_value)

        token_key2 = "auth-token"
        auth = parser_provider_auth(f"{token_key2}:{token_value}")
        self.assertEqual(auth.get(token_key2), token_value)

        username = "username"
        password = "password"
        auth = parser_provider_auth(
            f"username:{username},password:{password}"
        )
        self.assertEqual(auth.get("username"), username)
        self.assertEqual(auth.get("password"), password)

        # address_info.parameter = "not-real-device"
        # with self.assertRaises(AddressProviderException):
        #     AddressProviderHostName(address_info)


if __name__ == "__main__":
    unittest.main()
