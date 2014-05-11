from ec2 import EC2, authorize_group
from instances import (
    Instance, parse_instances, instances_to_create, instances_to_remove)
import click
from skipper.exceptions import ConfigurationException


class Host(object):
    def __init__(self, config=None):
        self._setup = False
        if config:
            self.add_config(config)

    def add_config(self, config):
        self.config = config
        self.ec2 = EC2(config['ACCESS_KEY'], config['SECRET_KEY'])

    @property
    def project_name(self):
        return "skipper_%s" % self.project.name

    def setup(self):
        # If we don't have a private key stored, should go ahead and generate
        # a new one. If one already exists, raise an error.
        if not self.config.get('PRIVATE_KEY'):
            key, created = self.ec2.get_or_create_key(self.project_name)
            if created:
                click.utils.echo("""No existing EC2 Key Pair can be found for %s.\nA new has been generated and stored in .skippercfg""" % self.project.name)
            if not created and not key.material:
                click.utils.echo("""An EC2 Key pair already exists for this project.\nPlease add the private key to .skippercfg""")
                raise ConfigurationException()
            if key.material:
                self.config['PRIVATE_KEY'] = key.material

        # Need to ensure we have a secrurity group setup with SSH access.
        # Retrive the group or create it.
        group = self.ec2.get_or_create_group(self.project_name)
        authorize_group(group, 'tcp', 22, 22, '0.0.0.0/0')
        self._setup = False

    def configure_instances(self, configuration):
        # TODO: Rename this. Terrible variable naming.
        instances = parse_instances(configuration)
        all_instances = []
        for each in instances:
            all_instances.append(Instance(each))
        # TODO: Should this be stored here instead?
        self.instances = all_instances
        return all_instances

    def deploy_instances(self):
        existing_instances = self.ec2.filter_instances(
            {'tag:project': self.project_name, 'tag:skipper': 'aye-aye'})

        # skipper instances to create.
        to_create = instances_to_create(self.instances, existing_instances)
        # ec2 instances that are no longer needed.
        to_remove = instances_to_remove(self.instances, existing_instances)

        for instance in to_create:
            created = self.ec2.create_instance(**instance.to_aws())
            created.add_tag('project', self.project_name)
            created.add_tag('uuid', instance.uuid)
            created.add_tag('skipper', 'aye-aye')

        for instance in to_remove:
            self.ec2.remove_instance(instance)

    def create_instance(self, instance):
        reservation = self.conn.run_instances(**{
            'image_id': 'ami-a73264ce',  # Ubuntu 12.04.1
            'instance_type': 't1.micro',
            'security_groups': ['skipper'],
            'key_name': 'skipper'
        })
        ec2_instance = reservation.instances[0]

        while ec2_instance.state != 'running':
            sleep(2)
            ec2_instance.update()
            print "Instance state: " + instance.state

        if ec2_instance.state == 'running':
            print('Instance is now running.')
            ec2_instance.add_tag('type', 'skipper')

        print("Waiting 15 seconds for good measure.")
        sleep(15)

        return ec2_instance

    def clean_up(self, instances):
        # TODO: Remove any instances that no longer exists.
        existing = self.conn.get_only_instances(filters={
            'tag:project': self.project_name,
            'tag:skipper': 'skipper'
        })


host = Host()
