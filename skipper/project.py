from services import parse_services, build_service
from instances import parse_instances


class Project(object):
    def __init__(self, name, host):
        if not name:
            raise Exception("A project must have a name.")
        self.name = name
        self.add_host(host)

        self.services = []
        self.instances = []

    def add_host(self, host):
        self.host = host
        host.project = self

    def configure_services(self, configuration):
        for name, details in configuration.items():
            self.services += parse_services(name, details)

    def configure_instances(self, configuration):
        for name, details in configuration.items():
            self.instances += parse_instances(name, details)

    def deploy(self):
        # Ensure the host is configured.
        if not self.host._setup:
            self.host.setup()
        # Build the services.
        for service in self.services:
            build_service(service)
