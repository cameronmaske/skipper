from django.db import models


class Host(models.Model):
    name = models.CharField(
        max_length=64, null=True, unique=True)
    address = models.CharField(
        max_length=128, null=True, unique=True, help_text='IP of the host.')
    port = models.SmallIntegerField(default=22)

    core_installed = models.BooleanField(default=False)
    docker_installed = models.BooleanField(default=False)
    docker_version = models.CharField(max_length=10, null=True)
    docker_port = models.SmallIntegerField(default=4243)

    logs = models.TextField(null=True)

    def __unicode__(self):
        return self.name

    def env(self):
        return {
            'host_string': self.address
        }
