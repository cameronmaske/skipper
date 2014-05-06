import click
import logging

from config import get_config
from settings import get_settings

logger = logging.getLogger('cli')


@click.group()
def cli():
    pass


@cli.command()
def deploy():
    config = get_config()
    from aws.host import Host
    from project import Project
    settings = get_settings()

    project = Project(name=settings['name'])
    host = Host(config=config, project=project)
    host.setup()
