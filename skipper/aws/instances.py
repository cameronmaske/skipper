from regions import REGIONS
from sizes import INSTANCE_SIZES

from skipper.logger import log
from skipper.instances import BaseInstance

from time import sleep
from paramiko import RSAKey


class Instance(BaseInstance):
    def __repr__(self):
        return '(AWSInstance: %s [%s])' % (self.uuid, self.region)

    def __init__(
            self, host, uuid, project_name, ec2, boto_instance,
            size="t1.micro", region="us-east-1"):
        self.host = host
        self.uuid = uuid
        self.project_name = project_name
        self.ec2 = ec2
        self.boto_instance = boto_instance
        self.aws_group = None
        self.valid_size(size)
        self.valid_region(region)

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
        if self.size != self.boto_instance.instance_type:
            # TOOD: Improve these log messages.
            log.info("Updating %s (%s -> %s)" % (
                self.uuid, self.boto_instance.instance_type, self.size))

            self.boto_instance.stop()
            log.info("Stopping %s" % self.uuid)
            while self.boto_instance.state != 'stopped':
                sleep(1)
                self.boto_instance.update()

            log.info("Updating %s" % self.uuid)
            self.boto_instance.modify_attribute(
                'instanceType', self.size
            )

            log.info("Starting %s" % self.uuid)
            self.boto_instance.start()

            while self.boto_instance.state != 'running':
                sleep(1)
                self.boto_instance.update()

    def delete(self):
        self.boto_instance.terminate()
        sleep(5)

    def status(self):
        return "[%s] Up and running - (%s)" % (self.uuid, self.boto_instance.public_dns_name)

    @property
    def fabric_params(self):
        return {
            'user': 'core',
            'host_string': self.boto_instance.public_dns_name,
            'key': self.host.private_key.read()
        }

    @property
    def tunnel_params(self):
        private_key = RSAKey(file_obj=self.host.private_key)

        return {
            'ssh_address': (self.boto_instance.public_dns_name, 22),
            'ssh_username': "ubuntu",
            'ssh_private_key': private_key,
            'remote_bind_address': ('127.0.0.1', 5555)
        }
