from services import Service


class NoSuchService(Exception):
    pass


class Project(object):

    def __init__(self, name, host):
        self.name = name
        host.project = self
        self.services = []
        self.groups = []

    def __repr__(self):
        return "Project (%s)" % self.name

    def make_service(self, name, **kwargs):
        service = Service(name=name, **kwargs)
        return service

    def get_service(self, name):
        """
        Retrievs a service by name.
        Taken from Fig.
        """
        for service in self.services:
            if service.name == name:
                return service

        raise NoSuchService("No such service %s" % name)

    def filter_services(self, names):
        """
        Retrives a list of services by names.
        If names is None, or an empty list return all.
        Taken from Fig.
        """

        if names is None or len(names) == 0:
            return self.services
        else:
            return [self.get_service(name) for name in names]
