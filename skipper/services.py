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

        self.client = None

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

    def containers(self, stopped=False, one_off=False):
        l = []
        for container in self.client.containers(all=stopped):
            uuid = get_container_uuid(container)
            try:
                (name, version, scale) = uuid.split("_", 3)
                if name == self.name:
                    l.append(Container.from_ps(self.client, container))
            except ValueError:
                continue
        return l

    def create_container(self, uuid):
        ports = self.loadbalance.values()
        return Container.create(
            self.client, image=self.repo.image, name=uuid, ports=ports)

    def run_containers(self):
        containers = self.containers()
        stream = self.client.pull(self.repo.image, stream=True)
        capture_events(stream)

        running = []
        for i in range(1, self.scale + 1):
            uuid = "%s_%s_%s" % (self.name, self.repo.tag, i)
            con = self.get_container(uuid, containers)

            if not con:
                con = self.create_container(uuid=uuid)
            else:
                # TODO: This
                if not self.container_up_to_date(con):
                    self.update_container(con)
            if not con.is_running:
                con.start(port_bindings={5000: None})
            running.append(con)
        return running

    def get_container(self, uuid, containers):
        for c in containers:
            if c.name == uuid:
                return c
        return None

    def container_up_to_date(self, container):
        # TOOD
        return True

    def update_container(self, container):
        pass

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


def get_container_uuid(container):
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
