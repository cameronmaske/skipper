def parse_services(name, details):
    services = [Service(name, **details)]
    return services


class Service(object):
    def __repr__(self):
        return '(Service: %s)' % self.name

    def __init__(self, name, **kwargs):
        self.name = name
