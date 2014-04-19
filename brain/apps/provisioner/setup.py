from fabric.api import run, sudo
from fabric.contrib import files


def has_docker():
    # Check if docker is installed on the host.
    output = run('which docker')
    if output:
        return True
    else:
        return False


def docker_version():
    version = run('docker --version')
    return version


def install_core():
    # Install some core dependencies required for Docker.
    run('apt-get -y update && apt-get -y upgrade')
    run('apt-get install -y curl')


def install_docker():
    # Install docker on the host.
    # Based on https://get.docker.io/ubuntu/
    run('curl -sL https://get.docker.io/ | sh')


def expose_docker():
    if not files.contains('/etc/default/docker', 'DOCKER_OPTS="-H tcp://0.0.0.0:4243 -H unix://var/run/docker.sock"'):
        files.append('/etc/default/docker', 'DOCKER_OPTS="-H tcp://0.0.0.0:4243 -H unix://var/run/docker.sock"', use_sudo=True)
        sudo('service docker restart')
