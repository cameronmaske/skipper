from django.db import models


class SSHKey(models.Model):
    private = models.TextField()
    public = models.TextField()
