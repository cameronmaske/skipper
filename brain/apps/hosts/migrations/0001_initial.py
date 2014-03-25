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
                ('host', models.CharField(help_text='IP/Host to connect to Docker', max_length=128, unique=True, null=True)),
                ('port', models.SmallIntegerField(default=4243, null=True)),
                ('ssh_setup', models.NullBooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
