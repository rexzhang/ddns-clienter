#!/usr/bin/env python

from logging import getLogger
from os import getenv

import click
import uvicorn

logger = getLogger(__name__)


@click.command()
@click.option(
    "-H",
    "--host",
    default="127.0.0.1",
    help="Bind socket to this host.  [default: 127.0.0.1]",
)
@click.option(
    "-P", "--port", default=8000, help="Bind socket to this port.  [default: 8000]"
)
@click.option("--dev", is_flag=True, help="for dev stage")
def cli(**cli_kwargs):
    kwargs = {
        "app": "ddns_clienter.asgi:application",
        "lifespan": "off",  # TODO: ASGI 'lifespan' protocol appears unsupported. Django 3.1.x
        "log_level": "info",
        "access_log": False,
    }
    kwargs.update(cli_kwargs)

    dev = kwargs.pop("dev", False)
    debug = getenv("DEBUG", False)
    if dev or debug:
        print("!!!Enter Development Stage...!!!")
        kwargs.update({"access_log": True, "reload": True})

    return uvicorn.run(**kwargs)


if __name__ == "__main__":
    cli()
