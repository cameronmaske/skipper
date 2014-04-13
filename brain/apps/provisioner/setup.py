from fabric.context_managers import settings
from StringIO import StringIO
from fabric.api import run, put, sudo, files


def install_ssh_public_key(host, public_key, user, password):
    # Ensure the Public Key is on the host.
    # Based on https://www.digitalocean.com/community/articles/how-to-set-up-ssh-keys--2
    with settings(**host.env()):
        put(StringIO(public_key), "~/.ssh/authorized_keys")
        host.ssh_enabled = True
        host.save()


def check_docker(host, private_key):
    # Check if docker is installed on the host.
    with settings(pkey=private_key, **host.env()):
        out = run('which docker')
        if out == '':
            return False
        return True


def install_core(host, private_key):
    # Install some core dependencies required for Docker.
    with settings(pkey=private_key, **host.env()):
        run('apt-get -y update && apt-get -y upgrade')
        run('apt-get install -y curl')


def install_docker(host, private_key):
    # Install docker on the host.
    # Based on https://get.docker.io/ubuntu/
    with settings(pkey=private_key, **host.env()):
        run('curl -sL https://get.docker.io/ | sh')


def configure_docker(host, private_key):
    with settings(pkey=private_key, **host.env()):
        if not files.contains('/etc/default/docker', 'DOCKER_OPTS="-H tcp://0.0.0.0:4243 -H unix://var/run/docker.sock"'):
            files.append('/etc/default/docker', 'DOCKER_OPTS="-H tcp://0.0.0.0:4243 -H unix://var/run/docker.sock"', use_sudo=True)
            sudo('service docker restart')
