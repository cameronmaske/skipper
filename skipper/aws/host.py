from skipper.hosts import BaseHost
from instances import Instance
from ec2 import EC2
from groups import AWSGroup


class Host(BaseHost):
    requirements = {
        'field': 'AWS',
        'message': (
            'As this is your first time running skipper, we need to store your'
            ' some AWS Security Credentials.\nPlease visit '
            'https://console.aws.amazon.com/iam/home?#security_credential'
            'Under Access Keys, click Create New Access Key.'),
        'keys': {
            'ACCESS_KEY': "Enter your Access Key ID",
            'SECRET_KEY': "Enter your Secret Access Key",
        }
    }

    def __init__(self, creds=None, project=None):
        self.creds = creds
        self.host = project
        self._ec2 = None

    def ec2(self):
        if not self._ec2:
            self._ec2 = EC2(
                access_key=self.creds['AWS']['ACCESS_KEY'],
                secret_key=self.creds['AWS']['SECRET_KEY'])
        return self._ec2

    def make_instances(self, name, **kwargs):
        instances = []
        scale = kwargs.pop('scale', 1)
        for i in range(1, scale + 1):
            instance = self.make_instance(
                name=name,
                project_name=self.project.name,
                scale=i,
                **kwargs
            )

            instances.append(instance)
        return instances

    def make_instance(self, name, project_name, **kwargs):
        return Instance(
            name=name,
            project_name=project_name,
            ec2=self.ec2(),
            **kwargs
        )

    def make_group(self, services, instances, loadbalancer):
        return AWSGroup(
            services=services,
            instances=instances,
            loadbalancer=loadbalancer,
            ec2=self.ec2(),
        )


host = Host()
