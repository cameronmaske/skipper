from skipper.hosts import BaseHost
from skipper.instances import InstanceNotFound
from skipper.logger import log
from skipper.ssh import ssh_tunnel
from skipper.fleet import Fleet
from skipper.ports import parse_ports_list
from skipper.exceptions import NoSuchService

from ec2 import EC2, authorize_group, revoke_group
from groups import Group
from instances import Instance
from regions import REGIONS
from helpers import (
    find_instance, find_machine_by_ip, outdated_rules)

from StringIO import StringIO
import click
from multiprocessing.dummy import Pool


class Host(BaseHost):
    def __init__(self, creds=None, project=None):
        self.creds = creds
        self.project = project
        self._ec2 = None

    def ec2(self):
        if not self._ec2:
            self._ec2 = EC2(**self.get_creds())
        return self._ec2

    @property
    def private_key(self):
        keys_path = self.get_keys_paths()
        with open(keys_path['private'], 'r') as f:
            contents = StringIO(f.read())
        return contents

    @property
    def public_key(self):
        keys_path = self.get_keys_paths()
        with open(keys_path['public'], 'r') as f:
            contents = StringIO(f.read())
        return contents

    def make_group(self, name, **kwargs):
        raw_ports = kwargs.pop("ports", {})
        ports = {
            "public": parse_ports_list(raw_ports.get("public", []))
        }

        return Group(
            name=name,
            ports=ports,
            **kwargs
        )

    def get_creds(self):
        """
        Returns a dictonary with of an access_key and secret_key. If not stored
        will prompt user to enter them.
        """
        access = self.creds.get('AWS', {}).get('ACCESS_KEY')
        secret = self.creds.get('AWS', {}).get('SECRET_KEY')
        if not access or not secret:
            message = (
                'The AWS Security Credentials stored are in complete. Please '
                're-enter them. \nYou can generate them on '
                'https://console.aws.amazon.com/iam/home?#security_credential'
                'Under Access Keys, click Create New Access Key.'
            )
        elif not access and not secret:
            message = (
                'As this is your first time running skipper, we need to store'
                ' your some AWS Security Credentials.\nPlease visit '
                'https://console.aws.amazon.com/iam/home?#security_credential'
                'Under Access Keys, click Create New Access Key.'
            )
        if not access or not secret:
            click.echo(message)
            self.creds['AWS']['ACCESS_KEY'] = click.prompt(
                "Enter your Access Key ID")
            self.creds['AWS']['SECRET_KEY'] = click.prompt(
                "Enter your Secret Access Key")
            self.creds.save()

        return {
            "access_key": self.creds['AWS']['ACCESS_KEY'],
            "secret_key": self.creds['AWS']['SECRET_KEY']
        }

    def get_keypair_name(self):
        """
        Returns the saved KeyPair name to use, else prompts the user to enter
        a desired name.
        """
        name = self.creds.get('AWS', {}).get('KEY_NAME')
        if not name:
            click.echo(
                "A KeyPair, consisting of an SSH public and private key is "
                "required for access to the cluster."
            )
            name = click.prompt(
                "Please enter the an existing KeyPair's name, or enter a "
                "unique name for yourself"
            )
            self.creds['AWS']['KEY_NAME'] = name
            self.creds.save()
        return name

    def get_or_import_key(self, region, name):
        """
        Attempts to retrieve a key pair else imports one locally.
        """
        key = self.ec2().get_key(region=region, name=name)
        if not key:
            public_key = self.public_key
            key = self.ec2().import_key(
                region=region,
                name=name,
                public_key_material=public_key.read()
            )
        return key

    def ps_instances(self):
        """
        Returns a lite dictonary version of all instances.
        """
        instances = self.all_instances()
        print_instances = []
        for instance in instances:
            group, scale = instance.uuid.split("_", 1)
            print_instances.append({
                "uuid": instance.uuid,
                "state": instance.boto_instance.state,
                "ip": instance.public_ip,
                "size": instance.boto_instance.instance_type,
                "group": group,
                "scale": scale,
                "region": instance.region,
            })
        return print_instances

    def __instances_by_region(self, region):
        """
        Private method used to return all associated instances with a region.
        Used in conjugation with a thread pool.
        """
        instances = self.ec2().filter_instances(
            region=region,
            filters={
                'tag:project': self.project.name
            },
            ignore=["terminated"]
        )
        return {
            'region': region,
            'instances': instances
        }

    def all_instances(self, **kwargs):
        """
        Returns all instances associated with the project (including stopped)
        """
        # Looks across all AWS regions, in parallel using a thread pool.
        pool = Pool(8)
        regions = kwargs.get('regions', REGIONS.keys())
        results = pool.map(self.__instances_by_region, regions)
        pool.close()
        pool.join()
        instances = []
        for result in results:
            for boto_instance in result['instances']:
                uuid = boto_instance.tags['uuid']
                instance = Instance(
                    host=self,
                    uuid=uuid,
                    project_name=self.project.name,
                    boto_instance=boto_instance,
                    size=boto_instance.instance_type,
                    region=result['region'],
                )
                instances.append(instance)
        return instances

    def get_or_create_instances(self, name, **kwargs):
        """
        Gets or creates an instances.
        """
        instances = []
        scale = kwargs.pop('scale', 1)
        region = kwargs.pop('region', "us-east-1")
        for i in range(1, scale + 1):
            uuid = "%s_%s" % (name, i)
            try:
                instance = self.get_instance(
                    uuid=uuid,
                    project_name=self.project.name,
                    region=region,
                    size=kwargs.get('size')
                )
                instance.update()
            except InstanceNotFound:
                instance = self.create_instance(
                    uuid=uuid,
                    project_name=self.project.name,
                    region=region,
                    size=kwargs.get('size')
                )
            instances.append(instance)
        return instances

    def get_instance(self, uuid, project_name, **kwargs):
        size = kwargs.get('size', "t1.micro")
        region = kwargs.get('region', "us-east-1")

        log.info("Checking for instance %s" % uuid)
        boto_instances = self.ec2().filter_instances(
            region=region,
            filters={
                'tag:uuid': uuid,
                'tag:project': project_name
            })

        try:
            boto_instance = boto_instances[0]
            instance = Instance(
                host=self,
                uuid=uuid,
                project_name=project_name,
                boto_instance=boto_instance,
                size=size,
                region=region,
            )
            log.info("Successfully found instance %s" % uuid)
            return instance
        except IndexError:
            log.info("Failed to find instance %s" % uuid)
            raise InstanceNotFound()

    def create_instance(self, uuid, project_name, **kwargs):
        size = kwargs.get('size', "t1.micro")
        region = kwargs.get('region', "us-east-1")

        group = self.ec2().get_or_create_group(
            region=region,
            name=project_name)[0]

        keypair_name = self.get_keypair_name()
        key = self.get_or_import_key(name=keypair_name, region=region)

        authorize_group(group, 'tcp', 22, 22, to_ip='0.0.0.0/0')
        authorize_group(group, 'tcp', 7001, 7001, to_group=group)
        authorize_group(group, 'tcp', 4001, 4001, to_group=group)

        log.info("Starting a new instance for %s" % uuid)

        config = """#cloud-config
coreos:
  etcd:
    # generate a new token for each unique cluster from https://discovery.etcd.io/new
    discovery: {}
    name: {}
    # multi-region and multi-cloud deployments need to use $public_ipv4
    addr: $private_ipv4:4001
    peer-addr: $private_ipv4:7001
  units:
    - name: etcd.service
      command: start
    - name: fleet.socket
      command: start
      content: |
        [Socket]
        ListenStream=6001
        Service=fleet.service
        [Install]
        WantedBy=sockets.target
    - name: fleet.service
      command: start
        """.format(self.get_etcd_token(), uuid)

        boto_instance = self.ec2().create_instance(
            region=region,
            instance_type=size,
            key_name=key.name,
            security_groups=[group.name],
            user_data=config.strip()
        )

        boto_instance.add_tag('name', uuid)
        boto_instance.add_tag('uuid', uuid)
        boto_instance.add_tag('project', project_name)

        instance = Instance(
            host=self,
            uuid=uuid,
            project_name=project_name,
            boto_instance=boto_instance,
            size=size,
            region=region,
        )

        log.info("Successfully created instance for %s" % uuid)
        return instance

    def ps_services(self):
        """
        Returns all services across a host.
        """
        instances = self.all_instances()

        with ssh_tunnel(instances[0].tunnel_params(port=6001)) as port:
            fleet = Fleet(port=port)
            machines = fleet.list_machines()
            states = fleet.list_states()

        return _ps_services(
            machines=machines, states=states, instances=instances)

    def run_service(self, instances, service, tag):
        """
        Runs a service across multiple instances.
        """
        instance = instances[0]

        with ssh_tunnel(instance.tunnel_params(port=6001)) as port:
            fleet = Fleet(port=port)
            machines = fleet.list_machines()
            for instance in instances:
                machine_id = find_machine_by_ip(
                    machines, instance.private_ip)["id"]
                for i in range(1, service.scale + 1):
                    scale = (instance.scale + i - 1)
                    name = "%s_%s" % (service.name, scale)
                    log.info(
                        'Checking for service %s on instance %s' %
                        (name, instance.uuid))
                    create = False
                    try:
                        existing = fleet.get_unit(name=name)
                        log.info(
                            'Found service %s, checking is up to date...'
                            % name)
                        if existing['options'] != service.fleet_params(tag=tag, scale=scale):
                            log.info(
                                'Existing service %s is outdated, removing...'
                                % name)

                            fleet.delete_unit(name=name)
                            create = True
                    except fleet.NotFound:
                        log.info('No existing service %s found' % name)
                        create = True

                    if create:
                        log.info('Creating service %s' % name)
                        fleet.create_unit(
                            machine_id=machine_id,
                            name=name,
                            options=service.fleet_params(tag=tag, scale=scale))
                        log.info('Successfully created service %s' % name)

    def configure_group(self, instances, group):
        """
        Opens ports publically for instances associated based on a group's
        settings.
        """
        ports = group.ports['public']
        if ports:
            ec2_group = self.ec2().get_or_create_group(
                region=group.region,
                name=group.name)[0]
            desired = []
            for port in ports:
                desired.append({
                    "ip_protocol": "tcp",
                    "from_port": str(port),
                    "to_port": str(port),
                    "to_ip": ['0.0.0.0/0']
                })
            outdated = outdated_rules(ec2_group.rules, desired)
            for old in outdated:
                revoke_group(ec2_group, **old)
            for new in desired:
                authorize_group(ec2_group, **new)
            for instance in instances:
                instance.add_group(ec2_group)


    def remove_service(self, uuid):
        """
        Stop a running service.
        """
        instances = self.all_instances()

        with ssh_tunnel(instances[0].tunnel_params(port=6001)) as port:
            fleet = Fleet(port=port)
            try:
                fleet.get_unit(name=uuid)
                fleet.delete_unit(name=uuid)
            except:
                raise NoSuchService()


host = Host()


def _ps_services(instances, machines, states):
    services = []
    for state in states:
        uuid, _ = state['name'].split('.')
        service, scale = uuid.split('_')
        _state = state['systemdSubState']
        instance = find_instance(instances, machines, state['machineID'])
        services.append({
            'uuid': uuid,
            'state': _state,
            'instance': instance.uuid,
            'ip': instance.public_ip,
            'service': service,
            'scale': scale
        })
    return services

