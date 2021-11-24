from logging import getLogger

import click

logger = getLogger(__name__)


@click.group()
def cli(**cli_kwargs):
    kwargs = cli_kwargs_parser(**cli_kwargs)
    logger.debug("uvicorn's kwargs:{}".format(kwargs))

    # do something
    return


@cli.command()
def command1():
    click.echo("command 1")


@cli.command()
def command2():
    click.echo("command 2")


@click.group()
def cli(**cli_kwargs):
    kwargs = cli_kwargs_parser(**cli_kwargs)
    logger.debug("cli's kwargs:{}".format(kwargs))

    # do something
    return


def cli_kwargs_parser(**kwargs) -> dict:
    return dict()


def main():
    cli()
