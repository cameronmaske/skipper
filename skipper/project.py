from services import parse_services, build_service


class Project(object):
    def __init__(self, name, host):
        if not name:
            raise Exception("A project must have a name.")
        self.name = name
        self.add_host(host)

        self.services = []

    def add_host(self, host):
        self.host = host
        host.project = self

    def configure_services(self, configuration):
        for name, details in configuration.items():
            self.services += parse_services(name, details)

    def configure_instances(self, configuration):
        self.host.configure_instances(configuration)

    @property
    def instances(self):
        self.host.instances

    def deploy(self):
        # Ensure the host is configured.
        if not self.host._setup:
            self.host.setup()
        # Build the services.
        for service in self.services:
            build_service(service)
        # Setup the instances.
        self.host.build_instances()

