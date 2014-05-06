def parse_services(name, details):
    services = [Service(name, **details)]
    return services


class Service(object):
    def __init__(self, name, **kwargs):
        self.name = name
