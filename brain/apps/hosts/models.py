from django.db import models


class Host(models.Model):
    name = models.CharField(
        max_length=64, null=True, unique=True)
    host = models.CharField(
        max_length=128, null=True, unique=True, help_text='IP/Host to connect to Docker')
    port = models.SmallIntegerField(null=True, default=4243)
    ssh_setup = models.NullBooleanField(null=True, default=False)

    def __unicode__(self):
        return self.name

    def env(self):
        return {}
