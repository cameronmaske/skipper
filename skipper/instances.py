from fabric.context_managers import settings
from fabric.api import run
from fabric.operations import open_shell


class InstanceError(Exception):
    pass


class InstanceNotFound(InstanceError):
    pass


class BaseInstance(object):
    def run_command(self, command):
        with settings(**self.fabric_params):
            run(command)

    def shell(self):
        with settings(**self.fabric_params):
            open_shell()

