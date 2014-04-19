# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, unique=True, null=True)),
                ('address', models.CharField(help_text='IP of the host.', max_length=128, unique=True, null=True)),
                ('port', models.SmallIntegerField(default=22)),
                ('core_installed', models.BooleanField(default=False)),
                ('docker_installed', models.BooleanField(default=False)),
                ('docker_version', models.CharField(max_length=10, null=True)),
                ('docker_port', models.SmallIntegerField(default=4243)),
                ('logs', models.TextField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
