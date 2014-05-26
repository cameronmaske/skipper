import click

from project import Project
from hosts import get_host
from creds import get_creds
from conf import get_conf


@click.group()
def cli():
    """
    Doc string describing the CLI at a glance.
    """


@cli.command()
@click.argument('groups', nargs=-1, required=False)
def deploy(groups):
    """
    Doc string describing the deploy.
    """
    creds = get_creds()
    conf = get_conf()
    host = get_host(conf.get('host', 'aws'))
    host.creds = creds
    project = Project(name=conf['name'], host=host)
    for group in conf['groups']:
        project.make_group(group)
    raise NotImplementedError("Deploy is still a work in progress.")
