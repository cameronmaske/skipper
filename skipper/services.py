from __future__ import unicode_literals
import json
import os
import docker
import requests
import re


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


def highest_tag_version(tags):
    # Deteremine the next tag based on existing tags.
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


def print_output(stream):
    events = []
    for line in stream:
        line = json.loads(line)
        if line.get('stream'):
            print(line['stream'])
            events.append(line['stream'])
    return events


def get_image_id_from_events(all_events):
    # Taken from Fig.
    # https://github.com/orchardup/fig/blob/master/fig/service.py
    image_id = None
    for event in all_events:
        match = re.search(r'Successfully built ([0-9a-f]+)', event)
        if match:
            image_id = match.group(1)
    return image_id


def image_in_tags(image_id, tags):
    for name, image in tags.items():
        if image_id[0:12] == image[0:12]:
            return name
    return None


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

    # Since we want to log out the the build process, we'll need to get the image
    # id created from the logs afterwards.
    stream = c.build(service.path, tag=service.registry['name'], rm=True, stream=True)
    all_events = print_output(stream)
    image_id = get_image_id_from_events(all_events)
    print("Successfully built %s" % (service.name))

    exists = image_in_tags(image_id, existing_tags)

    if exists:
        print("This build already exists, as %s:%s" % (service.registry['name'], exists))
        print("Aborting...")
        raise Exception("Already uploaded.")

    tag = generate_tag(next_version)
    print("Pushing %s:%s to %s:%s..." % (service.name, tag, service.registry['name'], tag))
    c.tag(image_id, repository=service.registry['name'], tag=tag)
    c.push(service.registry['name'])
    print("Successfully pushed %s:%s" % (service.name, tag))

    service.container = {
        'repo': service.registry['name'],
        'tag': tag
    }

