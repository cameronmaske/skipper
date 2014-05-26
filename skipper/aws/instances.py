from skipper.exceptions import ConfigurationException
from regions import REGIONS
from sizes import INSTANCE_SIZES

import docker
from time import sleep
from fabric.context_managers import settings, local_tunnel
from fabric.api import run, sudo
from fabric.contrib.files import contains, append


class Instance(object):
    def __init__(self, name, scale=1, size="t1.micro", region="us-east-1", loadbalance=None):
        self.name = name
        self.scale = scale
        self.valid_size(size)
        self.valid_region(region)
        self.loadbalance = loadbalance

    @property
    def uuid(self):
        # web_1_us-east-1
        return "%s_%s_%s" % (self.name, self.scale, self.region)

    def valid_size(self, size):
        if size in INSTANCE_SIZES.keys():
            self.size = size
        else:
            raise ConfigurationException("%s is not a valid size" % self.size)

    def valid_region(self, region):
        if region in REGIONS.keys():
            self.region = region
        else:
            raise ConfigurationException("%s is not a valid region" % self.region)

    def to_aws(self, project_name):
        image_id = REGIONS[self.region]['ami']

        return {
            'image_id': image_id,
            'instance_type': self.size,
            'security_groups': [project_name],
            'key_name': project_name,
            'region': self.region
        }

    def config_from_aws(self, boto_instance, private_key):
        self.fabric_params = {
            'user': 'ubuntu',
            'host_string': boto_instance.public_dns_name,
            'key': private_key,
        }

    def ensure_docker_installed(self):
        with settings(**self.fabric_params):
            installed = run('which docker', warn_only=True)
            if not installed:
                print("Attempting to install Docker.")
                sudo('sh -c "wget -qO- https://get.docker.io/gpg | apt-key add -"')
                sudo('sh -c "echo deb http://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list"')
                sudo('apt-get update')
                sudo('apt-get -y install linux-image-extra-virtual')
                sudo('apt-get -y install lxc-docker-0.11.0')
                sudo('apt-get update')
                sleep(10)

            if not contains('/etc/default/docker', 'DOCKER_OPTS="-H tcp://0.0.0.0:5555 -H unix://var/run/docker.sock"'):
                append('/etc/default/docker', 'DOCKER_OPTS="-H tcp://0.0.0.0:5555 -H unix://var/run/docker.sock"', use_sudo=True)
                sudo('service docker restart')

    def docker_client(self):
        with settings(**self.fabric_params):
            with local_tunnel(5555, bind_port=59432):
                client = docker.Client(base_url="http://localhost:59432")
                return client

