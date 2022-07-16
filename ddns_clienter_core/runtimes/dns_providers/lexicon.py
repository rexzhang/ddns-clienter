from logging import getLogger

from lexicon.client import Client
from lexicon.config import ConfigResolver

from .abs import DDNSProviderAbs, DDNSProviderException

logger = getLogger(__name__)


class DDNSProviderLexicon(DDNSProviderAbs):
    def _update_action(self, action: dict) -> dict:
        match self.provider_name_sub:
            case "cloudflare":
                action.update(
                    {
                        "cloudflare": {
                            "auth_token": self.task_config.provider_auth,
                        }
                    }
                )

        return action

    def _update_to_provider(self):
        update_success = True
        update_message = str()

        if self.task_config.ipv4:
            action = {
                "provider_name": self.provider_name_sub,
                "action": "update",
                "domain": self.task_config.domain,
                "type": "A",
                "name": self.task_config.host,
                "content": self.address_info.ipv4_address_str,
            }
            config = ConfigResolver().with_dict(self._update_action(action))
            if not Client(config).execute():
                update_success = False
                update_message += "update ipv4 failed"

        if self.task_config.ipv6:
            action = {
                "provider_name": self.provider_name_sub,
                "action": "update",
                "domain": self.task_config.domain,
                "type": "AAAA",
                "name": self.task_config.host,
                "content": self.address_info.ipv6_address_str,
            }
            config = ConfigResolver().with_dict(self._update_action(action))
            if Client(config).execute():
                update_success = False
                update_message += "update ipv6 failed"

        self.update_success = update_success
        self.update_message = update_message
