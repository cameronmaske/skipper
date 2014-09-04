from services import Service
from exceptions import NoSuchService
from ports import parse_ports_dict


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
        ports = kwargs.pop("ports", [])
        return Service(
            name=name,
            ports=parse_ports_dict(ports),
            **kwargs)

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

    def filter_groups(self, services):
        """
        Retrieves a list of groups based on their linked services.
        """
        groups = []
        for group in self.groups:
            for service in services:
                if service in group.services:
                    groups.append(group)
                    break
        return groups
