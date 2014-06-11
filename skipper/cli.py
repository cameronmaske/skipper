import click
from click.exceptions import FileError, ClickException

from project import Project, NoSuchService
from hosts import get_host
from creds import creds
from conf import get_conf
from logger import log
from builder import RepoNoPermission


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
@click.option('--silent', is_flag=True)
@pass_project
def cli(project, silent):
    """
    Doc string describing the CLI at a glance.
    """
    log.propagate = silent


@cli.command()
@click.argument('services', nargs=-1, required=False)
@pass_project
def build(project, services):
    """
    Build and upload service(s).
    """
    try:
        services = project.filter_services(services)
        for service in services:
            service.push()
    except (RepoNoPermission, NoSuchService) as e:
        raise ClickException(e.message)


@cli.command()
@click.argument('groups', nargs=-1, required=False)
@pass_project
def deploy(project, groups):
    """
    Configure and deploy group(s).
    """
    host = get_host(project.conf.get('host', 'aws'))
    host.creds = creds
    host.project = project
    for name, details in project.conf['groups'].items():

        services_names = details.pop('services', [])
        services = project.filter_services(services_names)

        instances = host.make_instances(name=name, **details)
        for instance in instances:
            try:
                instance.fetch()
            except:
                instance.deploy()


        # group = host.make_group(name=name)
        # group.attach_instances(instances)
        # group.build()

@cli.command()
@pass_project
def test(project):
    host = get_host(project.conf.get('host', 'aws'))
    host.creds = creds
    host.project = project

    instance = host.make_instance(name="web", project_name="demo")
    print instance
