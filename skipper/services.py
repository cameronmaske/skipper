from __future__ import unicode_literals
from logger import log, capture_events, EventError
from exceptions import (
    ServiceException, RepoNotFound, RepoNoPermission)

import re
import os
import docker
import requests


class Service(object):
    def __repr__(self):
        return '(Service: %s)' % self.name

    def __init__(self, name, repo, *args, **kwargs):
        self.name = name
        self.repo = repo
        self.build = kwargs.get('build')
        self.scale = kwargs.get('scale', 1)
        self.ports = kwargs.get('ports', {})
        self.client = docker.Client(os.environ.get('DOCKER_HOST'))

    def build_image(self):
        """
        Attempts to build an image for the service.

        Returns
            * A string of the docker image's id.
        """
        if self.build:
            log.info("Building %s..." % self.name)
            stream = self.client.build(self.build, rm=True, stream=True)
            all_events = capture_events(stream)
            image_id = image_id_from_events(all_events)
            log.info("Successfully built %s..." % self.name)
            return image_id
        else:
            raise ServiceException("Cannot build. No build path defined.")

    def clean_images(self, cutoff=10):
        """
        Cleans out older images. By default keeps the 10 most recent ones.
        """
        images = self.client.images(name=self.repo['name'], all=True)
        outdated = outdated_images(images=images, cutoff=cutoff)
        for image in outdated:
            self.client.remove_image(image, force=True)

    def push(self, tag):
        """
        Uploads a tagged version to the repo.
        """
        output = self.client.push(self.repo['name'], tag=tag, stream=True)
        try:
            capture_events(output)
        except EventError as e:
            if "401" in e.message:
                raise RepoNoPermission(
                    "You currently do not have access to %s.\nPlease try "
                    "logging in with `docker login`." % self.name)
            elif "403" in e.message:
                raise RepoNoPermission(
                    "You currently do not have access to %s.\nPlease make "
                    "sure you have the correct permissions" % self.name)

    def create_tag(self, tag):
        """
        Builds an image and tags it.

        Returns
            * A string of the docker image's id.
        """
        image_id = self.build_image()
        self.client.tag(image=image_id, repository=self.repo['name'], tag=tag)
        return image_id

    def get_remote_tags(self):
        """
        Retrieve all the tags associated with a repo.

        Returns
            * A list of tags, each has a layer and name.
        """
        r = requests.get(
            "https://%s/v1/repositories/%s/tags" % (
                self.repo.get('registry', "index.docker.io"),
                self.repo['name']))
        if r.status_code == 404:
            raise RepoNotFound(
                "No such repo %s" % (self.repo['name']))
        return r.json()

    def run_command(self, tag, scale=1):
        """
        Generates a run command for the service.

        Returns:
            * A string of the docker run command.
        """
        name = "%s_%s" % (self.name, scale)
        parts = ["/usr/bin/docker", "run", "--rm", "--name", name]
        if self.ports:
            parts += ["--publish"]
            for host, container in self.ports.items():
                if container:
                    parts += ["%s:%s" % (str(host), str(container))]
                else:
                    parts += [str(host)]

        parts += ["%s:%s" % (self.repo['name'], tag)]
        return " ".join(parts)

    def fleet_params(self, tag, scale=1):
        name = "%s_%s" % (self.name, scale)
        repo = "%s:%s" % (self.repo['name'], tag)
        return construct_fleet_options({
            "Unit": [
                {"Description": self.name},
                {"After": "docker.service"}
            ],
            "Service": [
                {"TimeoutStartSec": "0"},
                {"ExecStartPre": "-/usr/bin/docker kill %s" % name},
                {"ExecStartPre": "-/usr/bin/docker rm %s" % name},
                {"ExecStartPre": "/usr/bin/docker pull %s" % repo},
                {"ExecStart": self.run_command(tag=tag, scale=scale)},
                {"ExecStop": "/usr/bin/docker stop %s" % name}
            ]
        })


def construct_fleet_options(options):
    construct = []
    for section in ["Unit", "Service", "Socket"]:
        for option in options.get(section, []):
            for name, value in option.items():
                construct.append({
                    "section": section,
                    "name": name,
                    "value": value,
                })
    return construct


def outdated_images(images, cutoff=10):
    """
    Returns the oldest images to a cutoff (by default 10)

    Returns
        * A list of image names.

    """
    outdated = []
    sorted_images = sorted(
        images, key=lambda i: i['Created'])
    for image in sorted_images:
        for repo in image['RepoTags']:
            if repo not in outdated:
                outdated.append(repo)
                if len(outdated) >= cutoff:
                    return outdated
    return outdated


def image_id_from_events(all_events):
    """
    Extracts the image id for the build output.

    Returns
        * A string of the image id.

    Taken from Fig.
    https://github.com/orchardup/fig/blob/master/fig/service.py
    """
    image_id = None
    for event in all_events:
        match = re.search(r'Successfully built ([0-9a-f]+)', event)
        if match:
            image_id = match.group(1)
    return image_id


def split_tag_and_service(tagged_service):
    """
    Turns a string of a service name, possibly with a tag.

    Returns:
        * A string of the service's name
        * A string of the tag (can be None)
    """
    if ":" in tagged_service:
        service, tag = tagged_service.split(":", 1)
    else:
        service = tagged_service
        tag = None
    return service, tag


def split_tags_and_services(tagged_services):
    """
    Turns a list of service, possibily with tags, into a dictonary of
    services as the keys, and tags as the value.

    Example:

        ["foo:v1", "boo"]

        into...

        {
            "foo": "v1",
            "boo": None
        }
    """
    cleaned = {}
    for ts in tagged_services:
        service, tag = split_tag_and_service(ts)
        cleaned[service] = tag
    return cleaned
