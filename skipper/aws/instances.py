from regions import REGIONS
from sizes import INSTANCE_SIZES

from skipper.logger import log
from skipper.utils import extract_version

import docker
from time import sleep
from fabric.context_managers import settings, local_tunnel
from fabric.api import run, sudo
from fabric.contrib.files import contains, append


class InstanceNotFound(Exception):
    pass


class Instance(object):
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

    def ensure_docker_installed(self):
        docker_version = "1.0.0"
        with settings(**self.fabric_params):
            install_requirements = False
            install_docker = False
            docker_installed = run('which docker', warn_only=True)
            if docker_installed:
                docker_installed_version = extract_version(
                    run('docker --version', warn_only=True))
                if docker_installed_version != docker_version:
                    install_docker = True
            else:
                install_requirements = True
                install_docker = True

            if install_requirements:
                log.info("Attempting to install Docker (%s)" % docker_version)
                sudo('sh -c "wget -qO- https://get.docker.io/gpg | apt-key add -"')
                sudo('sh -c "echo deb http://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list"')
                sudo('apt-get update')
                sudo('apt-get -y install linux-image-extra-virtual')

            if install_docker:
                sudo(
                    "apt-get update -qq; apt-get install -y -o Dpkg::Options::="
                    "'--force-confdef' -o Dpkg::Options::='--force-confold'"
                    " lxc-docker-%s" % docker_version)
                sleep(5)

            if not contains('/etc/default/docker', 'DOCKER_OPTS="-H tcp://0.0.0.0:5555 -H unix://var/run/docker.sock"'):
                append('/etc/default/docker', 'DOCKER_OPTS="-H tcp://0.0.0.0:5555 -H unix://var/run/docker.sock"', use_sudo=True)
                sudo('service docker restart')

    def docker_test(self):
        # https://github.com/paramiko/paramiko/blob/master/demos/forward.py
        with settings(**self.fabric_params):
            with local_tunnel(5555, bind_port=59433):
                client = docker.Client(base_url="http://localhost:59433")
                print "containers"
                print client.containers()
                print "images"
                print client.images()
        print 'bla'

