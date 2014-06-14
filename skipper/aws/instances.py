from regions import REGIONS
from sizes import INSTANCE_SIZES

from skipper.logger import log
from skipper.instances import BaseInstance

from time import sleep
from paramiko import RSAKey
from StringIO import StringIO


class InstanceNotFound(Exception):
    pass


class Instance(BaseInstance):
    def __repr__(self):
        return '(AWSInstance: %s [%s])' % (self.uuid, self.region)

    def __init__(
            self, uuid, project_name, ec2, aws_instance, private_key,
            size="t1.micro", region="us-east-1"):
        self.uuid = uuid
        self.project_name = project_name
        self.ec2 = ec2
        self.aws_instance = aws_instance
        self.valid_size(size)
        self.valid_region(region)
        self.private_key = private_key

    def valid_size(self, size):
        if size in INSTANCE_SIZES.keys():
            self.size = size
        else:
            raise TypeError("%s is not a valid size" % self.size)

    def valid_region(self, region):
        if region in REGIONS.keys():
            self.region = region
        else:
            raise TypeError("%s is not a valid region" % self.region)

    def update(self):
        """
        Ensures the image has the correct size.
        """
        if self.size != self.aws_instance.instance_type:
            # TOOD: Improve these log messages.
            log.info("Updating %s (%s -> %s)" % (
                self.uuid, self.aws_instance.instance_type, self.size))

            self.aws_instance.stop()
            log.info("Stopping %s" % self.uuid)
            while self.aws_instance.state != 'stopped':
                sleep(1)
                self.aws_instance.update()

            log.info("Updating %s" % self.uuid)
            self.aws_instance.modify_attribute(
                'instanceType', self.size
            )

            log.info("Starting %s" % self.uuid)
            self.aws_instance.start()

            while self.aws_instance.state != 'running':
                sleep(1)
                self.aws_instance.update()

    @property
    def fabric_params(self):
        return {
            'user': 'ubuntu',
            'host_string': self.aws_instance.public_dns_name,
            'key': self.private_key
        }

    @property
    def tunnel_params(self):
        # Need to trick paramiko our string is a file.
        private_key_file = StringIO(self.private_key)
        private_key = RSAKey(file_obj=private_key_file)

        return {
            'ssh_address': (self.aws_instance.public_dns_name, 22),
            'ssh_username': "ubuntu",
            'ssh_private_key': private_key,
            'remote_bind_address': ('127.0.0.1', 5555)
        }
