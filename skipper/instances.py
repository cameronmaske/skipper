from fabric.context_managers import settings
from fabric.api import run, sudo
from fabric.operations import open_shell


class InstanceError(Exception):
    pass


class InstanceNotFound(InstanceError):
    pass


class BaseInstance(object):
    def run(self, command):
        with settings(**self.fabric_params):
            run(command)

    def sudo(self, command):
        with settings(**self.fabric_params):
            sudo(command)

    def shell(self):
        with settings(**self.fabric_params):
            open_shell()

