import yaml
from services import parse_services
from instances import parse_instances


def load_config():
    config = yaml.load(open('skipper.yml'))
    return config


def parse_config(config):
    pass


class Service(object):
    def __init__(self, name, **kwargs):
        self.name = name


class Project(object):
    def __init__(self):
        self.services = []
        self.instances = []

    def from_config(self, config):
        self.name = config['name']
        for name, details in config['services'].items():
            self.services += parse_services(name, details)

        for name, details in config['instances'].items():
            self.instances += parse_instances(name, details)


