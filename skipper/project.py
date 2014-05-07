from services import parse_services
from instances import parse_instances


class Service(object):
    def __init__(self, name, **kwargs):
        self.name = name


class Project(object):
    def __init__(self, name):
        if not name:
            raise Exception("A project must have a name.")
        self.name = name
        self.services = []
        self.instances = []

    def attach_host(self, host):
        self.host = host

    def from_config(self, config):
        self.name = config['name']
        for name, details in config['services'].items():
            self.services += parse_services(name, details)

        for name, details in config['instances'].items():
            self.instances += parse_instances(name, details)
