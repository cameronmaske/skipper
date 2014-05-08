from boto import ec2, exception
from time import sleep
import click


def authorize_group(group, ip_protocol, from_port, to_port, cidr_ip, retries=5):
    """
    Checks if a group has the correct protocol already authorized, else
    attempts to authorize them.

    Usage:
    >>> authorize_group(group, 'tcp', 22, 22, '0.0.0.0/0')
    """
    # TODO: Look at the rules already in a group. Saves an API call.
    # Tries 5 times by default. Fail safe if boto's API is down.
    for i in range(retries):
        try:
            group.authorize(ip_protocol, from_port, to_port, cidr_ip)
            break
        except exception.EC2ResponseError as e:
            if e.code == 'InvalidPermission.Duplicate':
                break
            # Wait one second before retrying.
            sleep(1)


class Host(object):
    def __init__(self, config=None):
        self._setup = False
        if config:
            self.add_config(config)

    def add_config(self, config):
        self.config = config
        self.conn = ec2.connection.EC2Connection(
            config['ACCESS_KEY'], config['SECRET_KEY'])

    def setup(self):
        # If we don't have a private key stored, should go ahead and generate
        # a new one. If one already exists, raise an error.
        project_name = "skipper_%s" % self.project.name
        if not self.config.get('PRIVATE_KEY'):
            # TODO: Abstract to get_or_create_key() + test
            try:
                key = self.conn.get_all_key_pairs(keynames=[project_name])[0]
                if not key.material:
                    click.utils.echo("""An EC2 Key pair already exists for this project.\nPlease add the private key to .skippercfg""")
                    raise Exception()
            except exception.EC2ResponseError as e:
                if e.code == 'InvalidKeyPair.NotFound':
                    click.utils.echo("""No existing EC2 Key Pair can be found for %s.
                        A new one will be generated and stored in .skippercfg""" % self.project.name)
                    key = self.conn.create_key_pair(project_name)

                    click.utils.echo("Succesfully generated a new EC2 Key Pair.")
                    self.config['PRIVATE_KEY'] = key.material
                else:
                    raise e
        # Need to ensure we have a secrurity group setup with SSH access.
        # Retrive the group or create it.
        # TODO: Abstract to get_or_create_group() + test
        try:
            group = self.conn.get_all_security_groups(
                filters={'group-name': project_name})[0]
        except IndexError:
            group = self.conn.create_security_group(
                project_name, "Skipper security group for %s" % self.project.name)

        authorize_group(group, 'tcp', 22, 22, '0.0.0.0/0')

        self._setup = False


host = Host()
