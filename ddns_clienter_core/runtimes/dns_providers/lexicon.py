from logging import getLogger

import lexicon.exceptions
from lexicon.client import Client
from lexicon.config import ConfigResolver

from .abs import DDNSProviderAbs, DDNSProviderException

logger = getLogger(__name__)


class DDNSProviderLexicon(DDNSProviderAbs):
    name = "lexicon"

    def _do_update(self, action: dict) -> (bool, str):
        action.update(
            {
                "provider_name": self.provider_name,
                "action": "update",
                "domain": self.task_config.domain,
                "name": self.task_config.host,
            }
        )

        extra_config_data = self.task_config.provider_auth.split(",")
        extra_config = dict()
        for data in extra_config_data:
            data = data.split(":")
            extra_config.update({data[0]: data[1]})
        action.update({self.provider_name: extra_config})

        try:
            result = Client(ConfigResolver().with_dict(action)).execute()
        except lexicon.exceptions.LexiconError as e:
            raise DDNSProviderException(f"LexiconError: {str(e)}")
        except Exception as e:
            raise DDNSProviderException(
                f"Call lexicon.client.Client() failed, {str(e)}"
            )

        if isinstance(result, bool):
            return result, ""

        return False, str(result)

    async def _update_to_provider(self) -> None:
        self.update_success = True
        self.update_message = ""

        if self.task_config.ipv4:
            action = {"type": "A", "content": self.address_info.ipv4_address_str}
            update_success, update_message = self._do_update(action)

            if not update_success:
                self.update_success = False
                self.update_message += "update ipv4 failed" + update_message

        if self.task_config.ipv6:
            action = {"type": "AAAA", "content": self.address_info.ipv6_address_str}
            update_success, update_message = self._do_update(action)

            if not update_success:
                self.update_success = False
                self.update_message += "update ipv6 failed" + update_message
