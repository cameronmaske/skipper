from boto import ec2, exception
from time import sleep
from regions import REGIONS


class EC2(object):
    """
    A client wrapper around boto's API. Helps to make a few AWS interactions
    a bit more elegant!

    Filters:
    http://docs.aws.amazon.com/AWSEC2/latest/APIReference/ApiReference-query-DescribeInstances.html
    """
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key

    def call(self, region='us-east-1'):
        return ec2.connect_to_region(
            region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key)

    def get_key(self, name, region='us-east-1'):
        """
        Attempts to get KeyPair based on a name.
        Returns the key
        """
        try:
            # Fun fact: Different regions handle this query very differently.
            # If you query any US region, if no key matches, it will raise an
            # exception.
            # If you query outside the US, it will return an empty list.
            try:
                keys = self.call(region).get_all_key_pairs(keynames=[name])
            except exception.EC2ResponseError as e:
                if e.code == 'InvalidKeyPair.NotFound':
                    keys = []
                else:
                    raise e
            key = keys[0]
        except IndexError:
            return None
        return key

    def import_key(self, name, public_key_material, region='us-east-1'):
        """
        Imports an existing public key to KeyPair
        """
        return self.call(region).import_key_pair(
            key_name=name,
            public_key_material=public_key_material)

    def create_key(self, name, region='us-east-1'):
        """
        Attempts to create a KeyPair based on a name.
        """
        key = self.call(region).create_key_pair(name)
        return key

    def get_or_create_group(self, name, description=None, region='us-east-1'):
        """
        Attempts to get or create a SecurityGroup based on a name.
        Returs the (group, created)
        group: is the SecurityGroup from EC2.
        created: is a boolean indicating if the group was created.
        """
        created = False
        try:
            group = self.call(region).get_all_security_groups(
                filters={'group-name': name})[0]
        except IndexError:
            created = True
            if not description:
                description = "Security group for %s" % name
            group = self.call(region).create_security_group(name, description)
        return group, created

    def filter_instances(self, filters, ignore=["terminated", "shutting-down"], region='us-east-1'):
        """
        Query for instances based on filters passed in.
        """
        instances = self.call(region).get_only_instances(filters=filters)

        # By default, we want to ignore removed instances.
        if ignore:
            instances = [i for i in instances if i.state not in ignore]

        return instances

    def create_instance(self, region='us-east-1', **kwargs):
        ami_image = REGIONS[region]['ami']
        reservation = self.call(region).run_instances(ami_image, **kwargs)
        instance = reservation.instances[0]

        while instance.state != 'running':
            sleep(1)
            instance.update()

        sleep(30)

        return instance

    def remove_instance(self, instance, region='us-east-1'):
        self.call(region).terminate_instances(instance_ids=[instance.id])


def authorize_group(group, ip_protocol, from_port, to_port, to_ip=None, to_group=None, retries=5):
    """
    Checks if a group has the correct protocol already authorized, else
    attempts to authorize them.

    Usage:
    >>> ec2 = EC2('access', 'secret')
    >>> group = ec2.get_or_create_group('skipper')
    >>> authorize_group(group, 'tcp', 22, 22, '0.0.0.0/0')
    """
    # TODO: Look at the rules already in a group. Saves an API call.
    # Tries 5 times by default. Fail safe if boto's API is down.
    for i in range(retries):
        try:
            group.authorize(ip_protocol, from_port, to_port, to_ip, to_group)
            break
        except exception.EC2ResponseError as e:
            if e.code == 'InvalidPermission.Duplicate':
                break
            # Wait one second before retrying.
            sleep(1)
