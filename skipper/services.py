from __future__ import unicode_literals


def parse_services(name, details):
    services = [Service(name, **details)]
    return services


class Service(object):
    def __repr__(self):
        return '(Service: %s)' % self.name

    def __init__(self, name, **kwargs):
        self.name = name
        self.path = kwargs.get('build')
        self.registry = kwargs.get('registry')


import os
import docker
import requests
import re
import sys
from fig.service import stream_output


def highest_tag_version(tags):
    # Deteremine the next tag based on exisitng tags.
    highest_version = 0
    for version in tags.keys():
        try:
            int_version = int(re.findall(r'v\d+', version)[0].replace('v', ''))
            if int_version > highest_version:
                highest_version = int_version
        except IndexError:
            pass
    return highest_version


class RepoNotFound(Exception):
    pass


def get_existing_tags(repo, registry="index.docker.io"):
    # TODO: Error handling.
    print("Checking %s for %s" % (registry, repo))
    r = requests.get("https://%s/v1/repositories/%s/tags" % (registry, repo))
    if r.status_code == 404:
        raise RepoNotFound("No repo yet created.")
    else:
        return format_tags(r.json())


def format_tags(tag_list):
    """
    Turn...

    [{"layer": "bla", "name": "latest"}, {"layer": "foo", "name": "v1"}]
    into
    {"latest": "bla", "v1": foo}
    """
    tag_dict = {}
    for tag in tag_list:
        tag_dict[tag['name']] = tag['layer']
    return tag_dict


def generate_tag(version):
    return "v%s" % version


def build_service(service):
    c = docker.Client(os.environ.get('DOCKER_HOST'))
    try:
        existing_tags = get_existing_tags(service.registry['name'])
        next_version = highest_tag_version(existing_tags) + 1
        print("Found %s existing builds for %s" % (len(existing_tags.keys()), service.name))
    except RepoNotFound:
        existing_tags = {}
        next_version = 1
        print("No existing builds can be found for the %s service." % (service.name))

    print("Building %s" % (service.name))
    # Taken from Fig.
    build_output = c.build(service.path, tag=service.registry['name'], rm=True, stream=True)
    all_events = stream_output(build_output, sys.stdout)

    image_id = None
    for event in all_events:
        if 'stream' in event:
            match = re.search(r'Successfully built ([0-9a-f]+)', event.get('stream', ''))
            if match:
                image_id = match.group(1)

    print("Successfully built %s" % (service.name))

    for name, image in existing_tags.items():
        if image_id == image[0: 12]:
            print("This build already exists as %s:%s." % (name, image))
            print("Aborting...")
            raise Exception("Already uploaded.")

    tag = generate_tag(next_version)
    print("Pushing %s:%s to %s:%s..." % (service.name, tag, service.registry['name'], tag))
    c.tag(image_id, repository=service.registry['name'], tag=tag)
    c.push(service.registry['name'])
    print("Successfully pushed %s:%s" % (service.name, tag))

