from skipper.groups import Group


class AWSGroup(Group):
    def __init__(self, name, project_name, services, instances, load_balanacer):
        self.name = name
        self.project_name = project_name
        self.services = services
        self.instances = instances
        self.load_balanacer = load_balanacer

