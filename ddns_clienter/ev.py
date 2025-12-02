from dataclasses import dataclass

from dataclass_wizard import EnvWizard
from django_vises.django_settings.env_var import EnvVarAbc


@dataclass
class EnvVar(EnvVarAbc, EnvWizard):
    class _(EnvWizard.Meta):
        env_file = True

    DATABASE_URI: str = "sqlite://db2.sqlite3"

    # project base
    CONFIG_TOML: str = "examples/ddns-clienter.toml"
    DATA_PATH: str = "."

    # project extra
    PBULIC_INSIDE_API: bool = True
    WORK_IN_CONTAINER: bool = False
    DISABLE_CRON: bool = False


EV = EnvVar()
