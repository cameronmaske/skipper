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
    from services import generate_services

    settings = get_settings()

    project = Project(name=settings['name'])
    host = Host(config=config, project=project)
    host.setup()

    services = project.generate_services(configuration=settings['services'])
    print services

    from skipper_aws import host
    from skipper.project import Project

    from skipper.config import get_config
    from skipper.settings import get_settings

    config = get_config()
    settings = get_settings()

    host.add_config(config)
    project = Project(name=settings['name'], host=host)
    project.configure_services(configuration=settings['services'])
    project.configure_instances(configuration=settings['instances'])
    project.deploy()

    project.services[0].scale(3)





