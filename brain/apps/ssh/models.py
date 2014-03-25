from os import remove

from fabric.api import local, hide
from django.db import models


class SSHKey(models.Model):
    private = models.TextField()
    public = models.TextField()

    def generate(self, passphrase=""):
        # Generate the private and pubilc keys.
        if len(passphrase) < 4:
            raise Exception("Passphrase needs to be greater then 4 characters long.")

        with hide("running", "stdout", "stderr"):
            local("ssh-keygen -f /tmp/id_rsa -t rsa -N '{}'".format(passphrase))
            self.private = local("cat /tmp/id_rsa", capture=True)
            self.public = local("cat /tmp/id_rsa.pub", capture=True)
        remove("/tmp/id_rsa")
        remove("/tmp/id_rsa.pub")
