from __future__ import unicode_literals
from loadbalancer.helpers import parse_ports
from builder import Repo, RepoNotFound
from logger import log, capture_events

import re
import os
import docker


class Service(object):
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
        self.loadbalance = parse_ports(loadbalance)
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
