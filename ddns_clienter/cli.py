from logging import getLogger
import os
import sys

import click
import uvicorn
from django.core import management

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
def runserver(**cli_kwargs):
    kwargs = {
        "app": "ddns_clienter.asgi:application",
        # "host": host,
        # "port": port,
        "lifespan": "off",
        "log_level": "info",
        "access_log": False,
    }
    kwargs.update(cli_kwargs)

    return uvicorn.run(**kwargs)


def main():
    cli()
