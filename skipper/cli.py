import click
from click.exceptions import FileError, ClickException


from project import Project
from services import split_tags_and_services
from instances import InstanceNotFound
from hosts import get_host
from creds import creds
from conf import get_conf
from logger import log
from formatter import instance_table
from exceptions import cli_exceptions


class CLIProject(Project):
    def __init__(self):
        try:
            self.conf = get_conf()
        except IOError as e:
            raise FileError(e.filename, hint='Are you in the right directory?')

        try:
            self.name = self.conf['name']
        except KeyError:
            raise ClickException('No name in skipper.yml')

        self.services = []
        for name, details in self.conf['services'].items():
            try:
                self.services.append(
                    self.make_service(name=name, **details))
            except TypeError as e:
                raise ClickException("%s: %s" % (name, e.message))


pass_project = click.make_pass_decorator(CLIProject, ensure=True)


@click.group()
@click.option('--silent', is_flag=True, help="Suppress logging messages.")
@pass_project
def cli(project, silent):
    """

    Doc string describing the CLI at a glance.
    """
    log.propagate = silent


@cli.command()
@click.argument('tagged_services', nargs=-1, required=False)
@pass_project
def tag(project, tagged_services):
    """
    Build and tag a service(s).

    Example:

        `skipper tag web:v11`

    """
    items = split_tags_and_services(tagged_services)
    services = project.filter_services(items.keys())
    with cli_exceptions():
        for service in services:
            tag = items.get(service.name)
            service.create_tag(tag=tag)


@cli.command()
@click.argument('tagged_services', nargs=-1, required=False)
@pass_project
def push(project, tagged_services):
    """
    Push a service's tag to it's registry.

    Example:

        `skipper push web:v11`

    """
    items = split_tags_and_services(tagged_services)
    services = project.filter_services(items.keys())
    with cli_exceptions():
        for service in services:
            tag = items.get(service.name)
            service.push(tag=tag)


@cli.command()
@click.argument('services', nargs=-1, required=False)
@click.option('--cutoff', default=10, help='Number of most recent images to keep.')
@pass_project
def clean(project, services, cutoff):
    """
    Removes older images locally for a services.

    Example:

        `skipper clean web --cutoff 20`

    """
    services = project.filter_services(services)
    with cli_exceptions():
        for service in services:
            service.clean_images(cutoff=cutoff)


@cli.group()
def instances():
    """Manages instances."""


@instances.command('deploy')
@pass_project
def instances_deploy(project):
    """
    Deploy all instances.
    """
    host = get_host(project.conf.get('host', 'aws'))
    host.creds = creds
    host.project = project
    host.check_requirements()
    for name, details in project.conf['groups'].items():
        host.get_or_create_instances(name=name, **details)


@instances.command('ps')
@pass_project
def instances_list(project):
    """
    Lists all instances.
    """
    host = get_host(project.conf.get('host', 'aws'))
    host.creds = creds
    host.project = project
    host.check_requirements()
    instances = host.all_instances()
    width, _ = click.get_terminal_size()
    click.echo(instance_table(instances, width))


@instances.command('remove')
@click.argument('uuid')
@pass_project
def instances_remove(project, uuid):
    """
    Remove a running instance.
    """
    host = get_host(project.conf.get('host', 'aws'))
    host.creds = creds
    host.project = project
    host.check_requirements()
    try:
        instance = host.get_instance(uuid, project.name)
    except InstanceNotFound:
        click.echo("Cannot find {}".format(uuid))
        return
    if click.confirm("Are you use want to remove this instance?"):
        instance.delete()
        click.echo("Instance has been successfully removed.")


@instances.command('ssh')
@click.argument('uuid')
@pass_project
def instances_ssh(project, uuid):
    """
    SSH into a running instance.
    """
    host = get_host(project.conf.get('host', 'aws'))
    host.creds = creds
    host.project = project
    host.check_requirements()
    try:
        instance = host.get_instance(uuid, project.name)
    except InstanceNotFound:
        click.echo("Cannot find {}".format(uuid))
        return
    instance.shell()
