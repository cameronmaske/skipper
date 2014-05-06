import click
from config import get_config


@click.group()
def cli():
    pass


@cli.command()
def deploy():
    config = get_config()
