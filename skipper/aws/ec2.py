from boto import ec2, exception
from time import sleep


class EC2(object):
    """
    A client wrapper around boto's API. Helps to make a few AWS interactions
    a bit more elegant!

    Filters:
    http://docs.aws.amazon.com/AWSEC2/latest/APIReference/ApiReference-query-DescribeInstances.html
    """
    def __init__(self, access_key, secret_key):
        self.conn = ec2.connection.EC2Connection(access_key, secret_key)

    def get_or_create_key(self, name):
        """
        Attempts to get or create a KeyPair based on a name.
        Returns the (key, created)
        key: is the KeyPair from EC2.
        created: is a boolean indicating if the group was created.
        """
        created = False
        try:
            key = self.conn.get_all_key_pairs(keynames=[name])[0]
        except exception.EC2ResponseError as e:
            if e.code == 'InvalidKeyPair.NotFound':
                key = self.conn.create_key_pair(self.project_name)
                created = True
            else:
                raise e
        return key, created

    def get_or_create_group(self, name, description=None):
        """
        Attempts to get or create a SecurityGroup based on a name.
        Returs the (group, created)
        group: is the SecurityGroup from EC2.
        created: is a boolean indicating if the group was created.
        """
        created = False
        try:
            group = self.conn.get_all_security_groups(
                filters={'group-name': name})[0]
        except IndexError:
            created = True
            if not description:
                description = "Security group for %s" % name
            group = self.conn.create_security_group(name, description)
        return group, created

    def filter_instances(self, filters, ignore_terminated=True):
        """
        Query for instances based on filters passed in.
        """
        instances = self.conn.get_only_instances(filters=filters)

        # By default, we want to ignore removed instances.
        if ignore_terminated:
            instances = [i for i in instances if i.state != "terminated"]

        return instances

    def create_instance(self, **kwargs):
        reservation = self.conn.run_instances(**kwargs)
        instance = reservation.instances[0]

        while instance.state != 'running':
            sleep(2)
            instance.update()
            print "Instance state: " + instance.state

        if instance.state == 'running':
            print('Instance is now running.')

        print("Waiting 15 seconds for good measure.")
        sleep(15)

        return instance

    def remove_instance(self, instance):
        self.conn.terminate_instances(instance_ids=[instance.id])

def authorize_group(group, ip_protocol, from_port, to_port, cidr_ip, retries=5):
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
            group.authorize(ip_protocol, from_port, to_port, cidr_ip)
            break
        except exception.EC2ResponseError as e:
            if e.code == 'InvalidPermission.Duplicate':
                break
            # Wait one second before retrying.
            sleep(1)
