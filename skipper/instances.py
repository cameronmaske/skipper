from skipper.utils import extract_version
from skipper.logger import log

from time import sleep
from os import path

from fabric.context_managers import settings, hide
from fabric.api import run, sudo
from fabric.contrib.files import contains, append, upload_template
from fabric.operations import open_shell

class InstanceError(Exception):
    pass


class BaseInstance(object):
    def ps(self, grep=None):
        with settings(**self.fabric_params):
            command = 'ps aux'
            if grep:
                command += '| grep %s' % grep
            run(command)

    def run_command(self, command):
        with settings(**self.fabric_params):
            run(command)

    def shell(self):
        with settings(**self.fabric_params):
            open_shell()

    def ensure_docker_installed(self):
        docker_version = "1.0.0"
        log.info("[%s] Checking Docker (%s) is installed" % (self.uuid, docker_version))
        with settings(hide('everything'), **self.fabric_params):
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
                log.info("[%s] Install Docker requirements" % (self.uuid))
                sudo('sh -c "wget -qO- https://get.docker.io/gpg | apt-key add -"')
                sudo(
                    'sh -c "echo deb http://get.docker.io/ubuntu docker main'
                    ' > /etc/apt/sources.list.d/docker.list"')
                sudo('apt-get update')
                sudo('apt-get -y install linux-image-extra-virtual')

            if install_docker:
                log.info("[%s] Installing Docker (%s)" % (self.uuid, docker_version))
                sudo(
                    "apt-get update -qq; apt-get install -y -o Dpkg::Options::="
                    "'--force-confdef' -o Dpkg::Options::='--force-confold'"
                    " lxc-docker-%s" % docker_version)
                sleep(5)
                log.info("[%s] Succesfully installed Docker (%s)" % (self.uuid, docker_version))

            if not contains('/etc/default/docker', 'DOCKER_OPTS="-H tcp://0.0.0.0:5555 -H unix://var/run/docker.sock"'):
                append('/etc/default/docker', 'DOCKER_OPTS="-H tcp://0.0.0.0:5555 -H unix://var/run/docker.sock"', use_sudo=True)
                sudo('service docker stop')
                sudo('service docker start')

    def ensure_supervisor_installed(self):
        log.info("[%s] Checking supervisor is installed" % (self.uuid))
        with settings(hide('everything'), **self.fabric_params):
            supervisor_install = run('which supervisord', warn_only=True)
            if not supervisor_install:
                log.info("[%s] Installing supervisor..." % (self.uuid))
                sudo('apt-get install -y supervisor')
                log.info("[%s] Succesfully installed supervisor" % (self.uuid))

    def ensure_nginx_installed(self):
        log.info("[%s] Checking nginx is installed" % (self.uuid))
        with settings(hide('everything'), **self.fabric_params):
            nginx = run('which nginx', warn_only=True)
            if not nginx:
                log.info("[%s] Installing nginx" % (self.uuid))
                sudo('apt-get install -y nginx')
                sudo('service nginx start')
                log.info("[%s] Succesfully installed nginx" % (self.uuid))

    def update_supervisor(self, programs):
        # http://supervisord.org/configuration.html#program-x-section-settings
        absolute_path = path.dirname(__file__)
        destination = "/etc/supervisor/conf.d/skipper.conf"

        context = {
            'programs': programs
        }

        log.info("[%s] Updating supervisor" % (self.uuid))
        with settings(hide('everything'), **self.fabric_params):
            upload_template(
                'supervisor.jinja',
                template_dir=absolute_path + '/templates',
                destination=destination,
                context=context,
                use_jinja=True,
                use_sudo=True)
            run('cat %s' % destination)
            sudo('service supervisor stop')
            sudo('service supervisor start')

    def update_nginx(self, containers, loadbalance):
        absolute_path = path.dirname(__file__)
        destination = "/etc/nginx/nginx.conf"

        context = {
            'containers': containers,
            'loadbalance': loadbalance,
        }

        log.info("[%s] Updating nginx" % (self.uuid))
        with settings(hide('everything'), **self.fabric_params):
            upload_template(
                'nginx.jinja',
                template_dir=absolute_path + '/templates',
                destination=destination,
                context=context,
                use_jinja=True,
                use_sudo=True)
            run('cat %s' % destination)
            sudo('/etc/init.d/nginx configtest')
            sudo('/etc/init.d/nginx reload')

    def get_or_create_containers(self, client, service):
        for i in range(1, service.scale + 1):
            uuid = "%s_%s_%s" % (service.name, service.repo.tag, i)



