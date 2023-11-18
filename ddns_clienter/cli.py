from logging import getLogger
from os import getenv

import click
import uvicorn

logger = getLogger(__name__)


@click.group()
def cli(**cli_kwargs):
    # do something
    return


@cli.command("runserver", help="Startup web UI server")
@click.option(
    "-H",
    "--host",
    default="127.0.0.1",
    help="Bind socket to this host.  [default: 127.0.0.1]",
)
@click.option(
    "-P", "--port", default=8000, help="Bind socket to this port.  [default: 8000]"
)
@click.option("--debug", is_flag=True)
def runserver(**cli_kwargs):
    kwargs = {
        "app": "ddns_clienter.asgi:application",
        "lifespan": "off",
        "log_level": "info",
        "access_log": False,
    }
    kwargs.update(cli_kwargs)

    debug = getenv("DEBUG")
    if debug is not None:
        kwargs.update({"debug": debug})

    return uvicorn.run(**kwargs)


def main():
    cli()
