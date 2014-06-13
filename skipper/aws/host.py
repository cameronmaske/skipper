from skipper.hosts import BaseHost
from instances import Instance, InstanceNotFound
from ec2 import EC2, authorize_group
from groups import AWSGroup
from skipper.logger import log


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
        self._keys = {}

    def check_keys(self, regions):
        """
        Checks if we have expected SSH keys required for the project.
        """
        for region in regions:
            field = self.requirements['field']
            if not self.creds[field].get(region):
                key, created = self.ec2().get_or_create_key(
                    region=region,
                    name=self.project.name
                )
                if created:
                    log.info(
                        "No existing EC2 Key Pair can be found for %s on %s.\n"
                        "A new has been generated and stored in .skippercfg"
                        % (self.project.name, region))
                if not created and not key.material:
                    log.error(
                        "An EC2 Key pair already exists for this project on %s.\n"
                        "Please add the private key to .skippercfg"
                        % region)
                    raise Exception
                if key.material:
                    self.creds[field][region] = key.material
                    self.creds.save()

            self.add_key(region, self.creds[field][region])

    def add_key(self, region, key):
        self._keys[region] = key

    def ec2(self):
        if not self._ec2:
            self._ec2 = EC2(
                access_key=self.creds['AWS']['ACCESS_KEY'],
                secret_key=self.creds['AWS']['SECRET_KEY'])
        return self._ec2

    def get_or_create_instances(self, name, **kwargs):
        instances = []
        scale = kwargs.pop('scale', 1)
        regions = kwargs.pop('regions', ["us-east-1"])
        for i in range(1, scale + 1):
            for region in regions:
                uuid = "%s_%s" % (name, scale)
                try:
                    instance = self.get_instance(
                        uuid=uuid,
                        project_name=self.project.name,
                        region=region,
                    )
                    instance.update()
                except InstanceNotFound:
                    instance = self.create_instance(
                        uuid=uuid,
                        project_name=self.project.name,
                        region=region,
                    )
                instances.append(instance)
        return instances

    def get_instance(self, uuid, project_name, **kwargs):
        size = kwargs.get('size', "t1.micro")
        region = kwargs.get('region', "us-east-1")

        aws_instances = self.ec2().filter_instances(
            region=region,
            filters={
                'tag:uuid': uuid,
                'tag:project': project_name
            })

        try:
            aws_instance = aws_instances[0]
            instance = Instance(
                uuid=uuid,
                project_name=project_name,
                ec2=self.ec2,
                aws_instance=aws_instance,
                private_key=self._keys[region],
                size=size,
                region=region,
            )
            return instance
        except IndexError:
            raise InstanceNotFound()

    def create_instance(self, uuid, project_name, **kwargs):
        size = kwargs.get('size', "t1.micro")
        region = kwargs.get('region', "us-east-1")

        group = self.ec2().get_or_create_group(
            region=region,
            name=project_name)[0]

        authorize_group(group, 'tcp', 22, 22, '0.0.0.0/0')

        aws_instance = self.ec2().create_instance(
            region=region,
            instance_type=size,
            key_name=project_name,
            security_groups=[project_name]
        )

        aws_instance.add_tag('uuid', uuid)
        aws_instance.add_tag('project', project_name)

        instance = Instance(
            uuid=uuid,
            project_name=project_name,
            ec2=self.ec2,
            aws_instance=aws_instance,
            private_key=self._keys[region],
            size=size,
            region=region,
        )
        return instance

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
