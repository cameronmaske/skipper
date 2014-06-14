import click
from click.exceptions import FileError, ClickException

import docker

from project import Project, NoSuchService
from hosts import get_host
from creds import creds
from conf import get_conf
from logger import log, capture_events
from builder import RepoNoPermission
from ssh import docker_tunnel


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
        host.check_keys(regions=details.get('regions', ["us-east-1"]))
        services_names = details.pop('services', [])
        services = project.filter_services(services_names)
        for service in services:
            service.push()

        instances = host.get_or_create_instances(name=name, **details)
        for instance in instances:
            instance.ensure_docker_installed()
            instance.ensure_supervisor_installed()
            programs = [
                {
                    'name': 'test',
                    'command': 'sleep 10',
                }
            ]
            instance.update_supervisor(programs)
            instance.ps()

        break

        with docker_tunnel(instance) as port:
            c = docker.Client(
                base_url="http://localhost:%s" % port)

            # Move this else where.
            containers = service.containers(client=c, stopped=True)

            for service in services:
                for i in range(1, service.scale + 1):
                    uuid = "%s_%s_%s" % (service.name, service.repo.tag, i)

                    # GET.
                    match = None
                    for container in containers:
                        if uuid == container.name:
                            match = container

                    if match:
                        print "Already running"
                        print match
                        if match.is_running:
                            match.stop()

                        match.remove()
                    else:
                        from containers import Container
                        # CREATE
                        stream = c.pull(service.repo.image, stream=True)
                        capture_events(stream)
                        # Container.create()
                        # Pass service params here.
                        con = Container.create(c, image=service.repo.image, name=uuid)
                        print con

                #     try:

                #         container = instance.get_container(
                #             uuid=uuid
                #         )
                #         if container.
                #     except:
                #         # Attempt to pull, then create.
                #         instance.create_container(
                #             uuid=uuid
                #         )
                # stream = c.pull(service.repo.image, stream=True)
                # capture_events(stream)
                # # for i in range(1, service.scale + 1):
                # #     uuid = "%s_%s" % (service.name, i)

                # containers = service.containers(client=c, stopped=True)
                # for c in containers:
                #     c.remove()

                # for i in range(1, service.scale + 1):
                #     uuid = "%s_%s" % (service.name, i)
                #     try:
                #         container = instance.get_container(
                #             uuid=uuid
                #         )
                #         if container.
                #     except:
                #         # Attempt to pull, then create.
                #         instance.create_container(
                #             uuid=uuid
                #         )


            # instance.get_container()

            # for service in services:
            #     service.pull(client=c)
            #     service.run(client=c)
            # instance.clean(client=c)

            # print service.loadbalance
            # print c.images()
            # print c.containers()
            # log.info('Pulling %s-%s' % (service.repo.name, service.repo.tag))
            # stream = c.pull(service.repo.name, tag="v11", stream=True)
            # events = capture_events(stream)
            # repo = "%s:%s" % (service.repo.name, "v11")
            # c_id = c.create_container(repo, name=service.name)
            # c.start(c_id, port_bindings=service.loadbalance[0])

        # group = host.make_group(
        #     name=name, instances=instances, services=services)
        # group.

        # print instances
        # print services


@cli.command()
@pass_project
def test(project):
    host = get_host(project.conf.get('host', 'aws'))
    host.creds = creds
    host.project = project
    host.check_requirements()

    all_regions = ["us-east-1", "us-west-1"]
    host.check_keys(regions=all_regions)

    from skipper.aws.instances import InstanceNotFound

    try:
        instance = host.get_instance(
            uuid="web_1", project_name="demo")
        instance.update()
    except InstanceNotFound:
        instance = host.create_instance(
            uuid="web_1", project_name="demo")

    instance.ensure_docker_installed()

    with docker_tunnel(instance) as port:
        client = docker.Client(
            base_url="http://localhost:%s" % port)
        print "containers"
        print client.containers()

    # instance = host.make_instance(name="web", project_name="demo")
    # print instance
    # try:
    #     instance.fetch()
    # except:
    #     instance.create()
