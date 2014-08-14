import requests
import docker
import os

from logger import capture_events, EventError


class RepoNoPermission(Exception):
    pass


class RepoNotFound(Exception):
    pass


class Repo(object):
    def __init__(self, name, registry="index.docker.io", tag=None):
        self.name = name
        self.registry = registry
        self.tag = tag

    @property
    def image(self):
        # Example: localhost:5000/registry-demo:v12
        if self.tag:
            return "%s:%s" % (self.name, self.tag)
        return self.name

    def get_tags(self):
        """
        Attempts to retrieve all the tags associated with a repo.
        """
        r = requests.get(
            "https://%s/v1/repositories/%s/tags" % (self.registry, self.name))
        if r.status_code == 404:
            raise RepoNotFound(
                "No such repo %s (on %s)" % (self.name, self.registry))
        return r.json()

    def upload(self, image_id, tag):
        """
        Uploads a tagged version to the repo.
        """
        client = docker.Client(os.environ.get('DOCKER_HOST'))
        client.tag(image=image_id, repository=self.name, tag=tag)
        output = client.push(self.name, stream=True)
        try:
            capture_events(output)
        except EventError as e:
            if '401' in e.message:
                raise RepoNoPermission(
                    'You currently do not have access to %s.\nPlease try '
                    'logging in with `docker login`.' % self.name)
            elif '403' in e.message:
                raise RepoNoPermission(
                    'You currently do not have access to %s.\nPlease make '
                    'sure you have the correct permissions' % self.name)
