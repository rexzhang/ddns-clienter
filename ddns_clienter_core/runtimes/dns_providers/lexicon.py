from logging import getLogger

from lexicon.client import Client
from lexicon.config import ConfigResolver

from .abs import DDNSProviderAbs, DDNSProviderException

logger = getLogger(__name__)


class DDNSProviderLexicon(DDNSProviderAbs):
    def _do_update(self, action: dict) -> (bool, str):
        action.update(
            {
                "provider_name": self.provider_name_sub,
                "action": "update",
                "domain": self.task_config.domain,
                "name": self.task_config.host,
                "content": self.address_info.ipv4_address_str,
            }
        )

        extra_config_data = self.task_config.provider_auth.split(",")
        extra_config = dict()
        for data in extra_config_data:
            data = data.split(":")
            extra_config.update({data[0]: data[1]})
        action.update({self.provider_name_sub: extra_config})

        result = Client(ConfigResolver().with_dict(action)).execute()
        if isinstance(result, bool):
            return result, ""

        return False, str(result)

    def _update_to_provider(self):
        self.update_success = True
        self.update_message = str()

        if self.task_config.ipv4:
            action = {"type": "A"}
            update_success, update_message = self._do_update(action)

            if not update_success:
                self.update_success = False
                self.update_message += "update ipv4 failed" + update_message

        if self.task_config.ipv6:
            action = {"type": "AAAA"}
            update_success, update_message = self._do_update(action)

            if not update_success:
                self.update_success = False
                self.update_message += "update ipv6 failed" + update_message
