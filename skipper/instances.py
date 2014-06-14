from skipper.utils import extract_version
from skipper.logger import log

from time import sleep
from os import path

from fabric.context_managers import settings
from fabric.api import run, sudo
from fabric.contrib.files import contains, append, upload_template


class InstanceError(Exception):
    pass


class BaseInstance(object):
    def ensure_supervisor_installed(self):
        with settings(**self.fabric_params):
            supervisor_install = run('which supervisord', warn_only=True)
            if not supervisor_install:
                sudo('apt-get install -y supervisor')

    def update_supervisor(self, programs):
        # http://supervisord.org/configuration.html#program-x-section-settings
        absolute_path = path.dirname(__file__)
        destination = "/etc/supervisor/conf.d/skipper.conf"

        context = {
            'programs': programs
        }

        with settings(**self.fabric_params):
            upload_template(
                'supervisor.jinja',
                template_dir=absolute_path + '/templates',
                destination=destination,
                context=context,
                use_jinja=True,
                use_sudo=True)

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
                sudo(
                    'sh -c "echo deb http://get.docker.io/ubuntu docker main'
                    ' > /etc/apt/sources.list.d/docker.list"')
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

    def ps(self, grep=None):
        with settings(**self.fabric_params):
            command = 'ps aux'
            if grep:
                command += '| grep %s' % grep
            run(command)


