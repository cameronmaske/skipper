class Group(object):
    def __init__(self, services, instances, load_balanacer):
        self.services = services
        self.instances = instances
        self.load_balanacer = load_balanacer
