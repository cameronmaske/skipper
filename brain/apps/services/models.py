from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=64, null=True, unique=True)
    scale = models.PositiveIntegerField(default=0)
    image = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name
