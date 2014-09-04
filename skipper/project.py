from services import Service
from exceptions import NoSuchService


class Project(object):

    def __init__(self, name, host):
        self.name = name
        host.project = self
        self.host = host
        self.services = []
        self.groups = []

    def __repr__(self):
        return "Project (%s)" % self.name

    def make_service(self, name, **kwargs):
        return Service(name=name, **kwargs)

    def get_service(self, name):
        """
        Taken from Fig.
        Retrievs a service by name.
        """
        for service in self.services:
            if service.name == name:
                return service

        raise NoSuchService("No such service %s" % name)

    def filter_services(self, names):
        """
        Taken from Fig.
        Retrives a list of services by names.
        If names is None, or an empty list return all.
        """

        if names is None or len(names) == 0:
            return self.services
        else:
            return [self.get_service(name) for name in names]
