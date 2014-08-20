from skipper.hosts import BaseHost
from skipper.instances import InstanceNotFound
from instances import Instance
from ec2 import EC2, authorize_group
from skipper.logger import log
from collections import OrderedDict

from StringIO import StringIO
import click


class Host(BaseHost):
    requirements = {
        'field': 'AWS',
        'message': (
            'As this is your first time running skipper, we need to store your'
            ' some AWS Security Credentials.\nPlease visit '
            'https://console.aws.amazon.com/iam/home?#security_credential'
            'Under Access Keys, click Create New Access Key.'),
        'keys': OrderedDict([
            ('ACCESS_KEY', "Enter your Access Key ID"),
            ('SECRET_KEY', "Enter your Secret Access Key"),
        ])
    }

    def __init__(self, creds=None, project=None):
        self.creds = creds
        self.project = project
        self._ec2 = None
        self._keys = {}

    def get_keypair_name(self):
        name = self.creds.get('AWS', {}).get('KEY_NAME')
        if not name:
            click.echo("A KeyPair, consisting of an SSH public and private key is required for access to the cluster.")
            name = click.prompt("Please enter the an existing KeyPair's name, or enter a unique name for yourself")
            self.creds['AWS']['KEY_NAME'] = name
            self.creds.save()
        return name

    @property
    def private_key(self):
        keys_path = self.get_keys_paths()
        with open(keys_path['private'], 'r') as f:
            contents = StringIO(f.read())
        return contents

    @property
    def public_key(self):
        keys_path = self.get_keys_paths()
        with open(keys_path['public'], 'r') as f:
            contents = StringIO(f.read())
        return contents

    def get_or_import_key(self, region, name):
        """ """
        key = self.ec2().get_key(region=region, name=name)
        if not key:
            public_key = self.public_key
            key = self.ec2().import_key(
                region=region,
                name=name,
                public_key_material=public_key.read()
            )
        return key

    def ec2(self):
        if not self._ec2:
            self._ec2 = EC2(
                access_key=self.creds['AWS']['ACCESS_KEY'],
                secret_key=self.creds['AWS']['SECRET_KEY'])
        return self._ec2

    def all_instances(self, **kwargs):
        region = kwargs.get('region', "us-east-1")
        boto_instances = self.ec2().filter_instances(
            region=region,
            filters={
                'tag:project': self.project.name
            },
            ignore=["terminated"])
        instances = []
        for aws in boto_instances:
            uuid = aws.tags['uuid']
            group, scale = uuid.split("_", 1)
            instances.append({
                "uuid": uuid,
                "state": aws.state,
                "ip": aws.ip_address,
                "size": aws.instance_type,
                "group": group,
                "scale": scale,
            })
        return instances

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

        boto_instances = self.ec2().filter_instances(
            region=region,
            filters={
                'tag:uuid': uuid,
                'tag:project': project_name
            })

        try:
            log.info("Checking for %s" % uuid)
            boto_instance = boto_instances[0]
            instance = Instance(
                host=self,
                uuid=uuid,
                project_name=project_name,
                ec2=self.ec2,
                boto_instance=boto_instance,
                size=size,
                region=region,
            )
            log.info("Successfully found %s" % uuid)
            return instance
        except IndexError:
            log.info("Failed to find %s" % uuid)
            raise InstanceNotFound()

    def create_instance(self, uuid, project_name, **kwargs):
        size = kwargs.get('size', "t1.micro")
        region = kwargs.get('region', "us-east-1")

        group = self.ec2().get_or_create_group(
            region=region,
            name=project_name)[0]

        keypair_name = self.get_keypair_name()
        key = self.get_or_import_key(name=keypair_name, region=region)

        authorize_group(group, 'tcp', 22, 22, to_ip='0.0.0.0/0')
        authorize_group(group, 'tcp', 7001, 7001, to_group=group)
        authorize_group(group, 'tcp', 4001, 7001, to_group=group)

        log.info("Starting a new instance for %s" % uuid)

        config = """#cloud-config
coreos:
  etcd:
    # generate a new token for each unique cluster from https://discovery.etcd.io/new
    discovery: {}
    # multi-region and multi-cloud deployments need to use $public_ipv4
    addr: $private_ipv4:4001
    peer-addr: $private_ipv4:7001
  units:
    - name: etcd.service
      command: start
    - name: fleet.service
      command: start""".format(self.creds['COREOS']['ETCD_TOKEN'])

        boto_instance = self.ec2().create_instance(
            region=region,
            instance_type=size,
            key_name=key.name,
            security_groups=[group.name],
            user_data=config.strip()
        )

        boto_instance.add_tag('uuid', uuid)
        boto_instance.add_tag('project', project_name)

        instance = Instance(
            host=self,
            uuid=uuid,
            project_name=project_name,
            ec2=self.ec2,
            boto_instance=boto_instance,
            size=size,
            region=region,
        )

        log.info("Successfully created instance for %s" % uuid)
        return instance


host = Host()
