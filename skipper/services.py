from __future__ import unicode_literals
from loadbalancer.helpers import parse_port
from builder import Repo, RepoNotFound
from logger import log, capture_events

import re
import os
import docker


from containers import Container


class Service(object):
    """
    Derived from fig's Service class.

    LICENSE: https://github.com/orchardup/fig/blob/master/LICENSE
    """
    def __repr__(self):
        return '(Service: %s)' % self.name

    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.build = kwargs.get('build')
        self._repo = None
        self.repo = kwargs.get('repo')
        if not self.repo:
            raise TypeError("An repo must be declared for each service.")

        self.scale = kwargs.get('scale', 1)
        loadbalance = kwargs.get('loadbalance', [])
        self.loadbalance = {}
        for port in loadbalance:
            if type(port) == str:
                port = parse_port(port)
            self.loadbalance.update(port)

    @property
    def repo(self):
        return self._repo

    @repo.setter
    def repo(self, repo):
        """
        Sets the repo.
        Turns "cameron/flask-web" into Repo(
            repo="cameron/flask-web"
            index="index.docker.io"
        )
        """
        if isinstance(repo, Repo):
            self._repo = repo
            return
        elif isinstance(repo, str):
            name = repo
            registry = "index.docker.io"
        else:
            try:
                name = repo['name']
            except:
                raise TypeError("Image doesn't contain a valid repo.")
            registry = repo.get('registry', "index.docker.io")

        self._repo = Repo(**{
            'name': name,
            'registry': registry
        })

    def build_image(self):
        if self.build:
            log.info("Building %s..." % self.name)
            client = docker.Client(os.environ.get('DOCKER_HOST'))
            stream = client.build(self.build, rm=True, stream=True)
            all_events = capture_events(stream)
            image_id = image_id_from_events(all_events)
            log.info("Successfully built %s..." % self.name)
            return image_id
        else:
            # TODO: Service exception?
            raise Exception("Cannot build. No build path defined.")

    def push(self):
        if self.build:
            image_id = self.build_image()
            self.upload(image_id)

    def upload(self, image_id):
        try:
            tags = self.repo.get_tags()
        except RepoNotFound:
            tags = {}

        exists = check_already_uploaded(image_id, tags)
        if exists:
            log.info("Already pushed %s:%s" % (self.name, exists))
            self.repo.tag = exists
        else:
            version = get_next_version(tags)
            tag = "v%s" % version
            log.info("Pushing %s:%s to %s:%s" % (self.name, tag, self.repo.name, tag))
            self.repo.upload(image_id, tag)
            self.repo.tag = tag
            log.info("Successfully pushed %s:%s" % (self.name, tag))

    def containers(self, client, stopped=False, one_off=False):
        l = []
        for container in client.containers(all=stopped):
            name = get_container_name(container)
            if not name:
                continue
            l.append(Container.from_ps(client, container))
        return l

    def start(self, **options):
        for c in self.containers(stopped=True):
            if not c.is_running:
                log.info("Starting %s..." % c.name)
                self.start_container(c, **options)

    def stop(self, **options):
        for c in self.containers():
            log.info("Stopping %s..." % c.name)
            c.stop(**options)

    def kill(self, **options):
        for c in self.containers():
            log.info("Killing %s..." % c.name)
            c.kill(**options)

    def scale(self, desired_num):
        """
        Adjusts the number of containers to the specified number and ensures they are running.

        - creates containers until there are at least `desired_num`
        - stops containers until there are at most `desired_num` running
        - starts containers until there are at least `desired_num` running
        - removes all stopped containers
        """
        if not self.can_be_scaled():
            raise CannotBeScaledError()

        # Create enough containers
        containers = self.containers(stopped=True)
        while len(containers) < desired_num:
            containers.append(self.create_container())

        running_containers = []
        stopped_containers = []
        for c in containers:
            if c.is_running:
                running_containers.append(c)
            else:
                stopped_containers.append(c)
        running_containers.sort(key=lambda c: c.number)
        stopped_containers.sort(key=lambda c: c.number)

        # Stop containers
        while len(running_containers) > desired_num:
            c = running_containers.pop()
            log.info("Stopping %s..." % c.name)
            c.stop(timeout=1)
            stopped_containers.append(c)

        # Start containers
        while len(running_containers) < desired_num:
            c = stopped_containers.pop(0)
            log.info("Starting %s..." % c.name)
            self.start_container(c)
            running_containers.append(c)

        self.remove_stopped()

    def remove_stopped(self, **options):
        for c in self.containers(stopped=True):
            if not c.is_running:
                log.info("Removing %s..." % c.name)
                c.remove(**options)

    def create_container(self, one_off=False, **override_options):
        """
        Create a container for this service. If the image doesn't exist, attempt to pull
        it.
        """
        container_options = self._get_container_create_options(override_options, one_off=one_off)
        try:
            return Container.create(self.client, **container_options)
        except APIError as e:
            if e.response.status_code == 404 and e.explanation and 'No such image' in str(e.explanation):
                log.info('Pulling image %s...' % container_options['image'])
                output = self.client.pull(container_options['image'], stream=True)
                stream_output(output, sys.stdout)
                return Container.create(self.client, **container_options)
            raise

    def recreate_containers(self, **override_options):
        """
        If a container for this service doesn't exist, create and start one. If there are
        any, stop them, create+start new ones, and remove the old containers.
        """
        containers = self.containers(stopped=True)

        if len(containers) == 0:
            log.info("Creating %s..." % self.next_container_name())
            container = self.create_container(**override_options)
            self.start_container(container)
            return [(None, container)]
        else:
            tuples = []

            for c in containers:
                log.info("Recreating %s..." % c.name)
                tuples.append(self.recreate_container(c, **override_options))

            return tuples

    def recreate_container(self, container, **override_options):
        if container.is_running:
            container.stop(timeout=1)

        intermediate_container = Container.create(
            self.client,
            image=container.image,
            volumes_from=container.id,
            entrypoint=['echo'],
            command=[],
        )
        intermediate_container.start(volumes_from=container.id)
        intermediate_container.wait()
        container.remove()

        options = dict(override_options)
        options['volumes_from'] = intermediate_container.id
        new_container = self.create_container(**options)
        self.start_container(new_container, volumes_from=intermediate_container.id)

        intermediate_container.remove()

        return (intermediate_container, new_container)

    def start_container(self, container=None, volumes_from=None, **override_options):
        if container is None:
            container = self.create_container(**override_options)

        options = self.options.copy()
        options.update(override_options)

        port_bindings = {}

        if options.get('ports', None) is not None:
            for port in options['ports']:
                port = str(port)
                if ':' in port:
                    external_port, internal_port = port.split(':', 1)
                else:
                    external_port, internal_port = (None, port)

                port_bindings[internal_port] = external_port

        volume_bindings = {}

        if options.get('volumes', None) is not None:
            for volume in options['volumes']:
                if ':' in volume:
                    external_dir, internal_dir = volume.split(':')
                    volume_bindings[os.path.abspath(external_dir)] = {
                        'bind': internal_dir,
                        'ro': False,
                    }

        privileged = options.get('privileged', False)

        container.start(
            links=self._get_links(link_to_self=override_options.get('one_off', False)),
            port_bindings=port_bindings,
            binds=volume_bindings,
            volumes_from=volumes_from,
            privileged=privileged,
        )
        return container

def get_container_name(container):
    if not container.get('Name') and not container.get('Names'):
        return None
    # inspect
    if 'Name' in container:
        return container['Name']
    # ps
    for name in container['Names']:
        if len(name.split('/')) == 2:
            return name[1:]


def check_already_uploaded(image_id, tags):
    """
    Based on the image id and the tags, check if the service is already
    uploaded.

    image_id = 12346
    tags = [{"layer": "12346", "name": "latest"}, {"layer": "14445", "name": "v1"}]
    """
    for tag in tags:
        if tag['layer'][0:8] == image_id[0:8]:
            return tag['name']
    return None


def get_next_version(tags):
    """
    Based on the tags passed in, work out the next tag to use.
    E.g,
    tags = [{"layer": "12346", "name": "v1"}, {"layer": "14445", "name": "v2"}]
    return "v3"
    """
    highest_version = 0
    for tag in tags:
        try:
            int_version = int(re.findall(r'v\d+', tag['name'])[0].replace('v', ''))
            if int_version > highest_version:
                highest_version = int_version
        except IndexError:
            pass
    return (highest_version + 1)


def image_id_from_events(all_events):
    """
    Extracts the image id for the build output.

    Taken from Fig.
    https://github.com/orchardup/fig/blob/master/fig/service.py
    """
    image_id = None
    for event in all_events:
        match = re.search(r'Successfully built ([0-9a-f]+)', event)
        if match:
            image_id = match.group(1)
    return image_id
