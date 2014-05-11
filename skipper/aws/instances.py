from skipper.exceptions import ConfigurationException
from regions import REGIONS
from sizes import INSTANCE_SIZES


def instances_to_create(instances, existing_instances):
    to_create = []
    for instance in instances:
        match = False
        for existing in existing_instances:
            if existing.tags['uuid'] == instance.uuid:
                match = True
        if not match:
            to_create.append(instance)
    return to_create


def instances_to_remove(instances, existing_instances):
    to_remove = []
    for existing in existing_instances:
        match = False
        for instance in instances:
            if existing.tags['uuid'] == instance.uuid:
                match = True
        if not match:
            to_remove.append(existing)
    return to_remove


def parse_port(ports_string):
    # TODO: Make this part of skipper's core.
    """
    Turns "80:80" -> {80: 80}
    """
    guest, host = ports_string.split(':')
    ports = {}
    ports[int(guest)] = int(host)
    return ports


def parse_settings(settings):
    instances = []
    for name, details in settings.items():
        for scale in range(1, details.get('scale', 1) + 1):
            for region in details.get('regions', ['us-east-1']):
                loadbalance = [parse_port(l) for l in details.get('loadbalance', [])]
                instances.append({
                    'name': name,
                    'scale': scale,
                    'size': details.get('size', 't1.micro'),
                    'region': region,
                    'loadbalance': loadbalance
                })
    return instances


class Instance(object):
    def __init__(self, name, scale=1, size="t1.micro", region="us-east-1", loadbalance=None):
        self.name = name
        self.scale = scale
        self.valid_size(size)
        self.valid_region(region)
        self.loadbalance = loadbalance

    @property
    def uuid(self):
        # web_1_us-east-1
        return "%s_%s_%s" % (self.name, self.scale, self.region)

    def valid_size(self, size):
        if size in INSTANCE_SIZES.keys():
            self.size = size
        else:
            raise ConfigurationException("%s is not a valid size" % self.size)

    def valid_region(self, region):
        if region in REGIONS.keys():
            self.region = region
        else:
            raise ConfigurationException("%s is not a valid region" % self.region)

    def to_aws(self):
        image_id = REGIONS[self.region]['ami']

        return {
            'image_id': image_id,
            'instance_type': self.size,
            'security_groups': ['skipper'],
            'key_name': 'skipper'
        }

