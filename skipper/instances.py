# All possible regions of EC2 instances.
# http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html
REGIONS = {
    'ap-northeast-1': "Asia Pacific (Tokyo) Region",
    'ap-southeast-1': "Asia Pacific (Singapore) Region",
    'ap-southeast-2': "Asia Pacific (Sydney) Region",
    'eu-west-1': "EU (Ireland) Region",
    'sa-east-1': "South America (Sao Paulo) Region",
    'us-east-1': "US East (Northern Virginia) Region",
    'us-west-1': "US West (Northern California) Region",
    'us-west-2': "US West (Oregon) Region"
}


def parse_instances(name, details):
    instances = []
    for i in range(details.get('scale', 1)):
        instances.append(Instance(name, i, **details))
    return instances


class InstanceError(Exception):
    pass


class Instance(object):
    def __init__(self, name, count, ec2=None, **kwargs):
        self.name = name
        self.count = count
        self.uuid = "%s_%s" % (name, count)
        region = kwargs.pop('region', 'us-east-1')
        self.validate_region(region)
        self.region = region
        self.size = kwargs.pop('size', 't1.micro')
        self.ec2 = ec2

    def validate_region(self, region):
        if region not in REGIONS.keys():
            raise InstanceError("%s is not a valid region." % region)
