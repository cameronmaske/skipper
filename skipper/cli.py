import click
from click.exceptions import FileError, ClickException

from project import Project, NoSuchService
from hosts import get_host
from creds import creds
from conf import get_conf
from logger import log
from builder import RepoNoPermission


class CLIProject(Project):
    exception = ClickException

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

        self.host = get_host(self.conf.get('host', 'aws'))
        self.host.creds = creds


pass_config = click.make_pass_decorator(CLIProject, ensure=True)


@click.group()
@click.option('--silent', is_flag=True)
@pass_config
def cli(project, silent):
    """
    Doc string describing the CLI at a glance.
    """
    log.propagate = silent


@cli.command()
@click.argument('services', nargs=-1, required=False)
@pass_config
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
