import click

from aws.host import host
from aws.config import requirements
from project import Project
from config import get_config
from settings import get_settings


@click.group()
def cli():
    pass


@cli.command()
def deploy():
    config = get_config(requirements=requirements)
    settings = get_settings()

    host.add_config(config)
    project = Project(name=settings['name'], host=host)
    project.configure_services(configuration=settings['services'])
    project.configure_instances(configuration=settings['instances'])
    project.deploy()

    project.services[0].scale(3)





