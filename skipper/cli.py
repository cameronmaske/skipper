import click
from click.exceptions import FileError, ClickException


from project import Project
from services import split_tags_and_services
from instances import InstanceNotFound
from hosts import get_host
from creds import creds
from conf import get_conf
from logger import log
from formatter import instance_table, service_table
from exceptions import cli_exceptions, NoSuchService


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
            except (TypeError, ValueError) as e:
                raise ClickException("%s: %s" % (name, e.message))

        self.host = get_host(self.conf.get('host', 'aws'))
        self.host.creds = creds
        self.host.project = self

        self.groups = []
        for name, details in self.conf['groups'].items():
            try:
                self.groups.append(
                    self.host.make_group(
                        name=name,
                        region=self.conf.get('region'),
                        **details))
            except (TypeError, ValueError) as e:
                raise ClickException("%s: %s" % (name, e.message))


pass_project = click.make_pass_decorator(CLIProject, ensure=True)


@click.group()
@click.option('--silent', is_flag=True, help="Suppress logging messages.")
@click.version_option()
@pass_project
def cli(project, silent):
    """
    A docker orchestration tool to build, deploy and
    manage your applications.

    """
    log.propagate = silent


@cli.command()
@pass_project
def ps(project):
    """
    List all services running across the cluster.

    """
    services = project.host.ps_services()
    width, _ = click.get_terminal_size()
    click.echo(service_table(services, width))


@cli.command()
@click.argument('uuid')
@pass_project
def remove(project, uuid):
    """
    Remove a running service by uuid.

    Example:

        `skipper remove web_1`

    """
    try:
        click.echo('Checking for service {}'.format(uuid))
        project.host.remove_service(uuid)
        click.echo('Successfully removed service {}'.format(uuid))
    except NoSuchService:
        click.echo("Cannot find service {}".format(uuid))
        return


@cli.command()
@click.argument('tagged_services', nargs=-1, required=False)
@pass_project
def tag(project, tagged_services):
    """
    Build and tag services.

    Example:

        `skipper tag web:v11`

    """
    items = split_tags_and_services(tagged_services)
    services = project.filter_services(items.keys())
    with cli_exceptions():
        for service in services:
            tag = items[service.name]
            service.create_tag(tag=tag)


@cli.command()
@click.argument('tagged_services', nargs=-1, required=False)
@pass_project
def push(project, tagged_services):
    """
    Push tagged services to their registries.

    Example:

        `skipper push web:v11 celery:v1`

    """
    items = split_tags_and_services(tagged_services)
    services = project.filter_services(items.keys())
    with cli_exceptions():
        for service in services:
            tag = items[service.name]
            service.push(tag=tag)


@cli.command()
@click.argument('tagged_services', nargs=-1, required=False)
@pass_project
def deploy(project, tagged_services):
    """
    Deploy services across the cluster.

    Example:

        `skipper deploy web:v11 celery:v2`

    """
    items = split_tags_and_services(tagged_services)
    services = project.filter_services(items.keys())
    with cli_exceptions():
        for service in services:
            groups = project.filter_groups(
                services=[s.name for s in services])
            for group in groups:
                instances = project.host.get_or_create_instances(
                    name=group.name, **group.details())
                project.host.configure_group(instances, group)
                tag = items[service.name]
                project.host.run_service(
                    instances=instances,
                    service=service,
                    tag=tag)
    click.echo('Deployment was successful')


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
    for group in project.groups:
        instances = project.host.get_or_create_instances(
            name=group.name, **group.details())
        project.host.configure_group(instances, group)


@instances.command('ps')
@pass_project
def instances_ps(project):
    """
    Lists all instances.
    """
    instances = project.host.ps_instances()
    width, _ = click.get_terminal_size()
    click.echo(instance_table(instances, width))


@instances.command('remove')
@click.argument('uuid')
@pass_project
def instances_remove(project, uuid):
    """
    Remove a running instance.
    """
    try:
        instance = project.host.get_instance(uuid, project.name)
    except InstanceNotFound:
        click.echo("Cannot find {}".format(uuid))
        return
    if click.confirm("Are you use want to remove this instance?"):
        try:
            instance.unregister()
        except:
            pass
        instance.delete()
        click.echo("Instance has been successfully removed.")


@instances.command('ssh')
@click.argument('uuid')
@pass_project
def instances_ssh(project, uuid):
    """
    SSH into a running instance.
    """
    try:
        instance = project.host.get_instance(uuid, project.name)
    except InstanceNotFound:
        click.echo("Cannot find {}".format(uuid))
        return
    instance.shell()
