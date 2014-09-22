# All possible regions of EC2 instances.
# https://coreos.com/docs/running-coreos/cloud-providers/ec2/
# Includes the humanize name of the region and the CoreOS AMI

REGIONS = {
    'ap-northeast-1': {
        'name': "Asia Pacific (Tokyo) Region",
        'ami': "ami-39062938"
    },
    'ap-southeast-1': {
        'name': "Asia Pacific (Singapore) Region",
        'ami': "ami-aee1c5fc"
    },
    'ap-southeast-2': {
        'name': "Asia Pacific (Sydney) Region",
        'ami': "ami-0546253f"
    },
    'eu-west-1': {
        'name': "EU (Ireland) Region",
        'ami': "ami-428d2a35"
    },
    'sa-east-1': {
        'name': "South America (Sao Paulo) Region",
        'ami': "ami-d96cc6c4"
    },
    'us-east-1': {
        'name': "US East (Northern Virginia) Region",
        'ami': "ami-1a862f72"
    },
    'us-west-1': {
        'name': "US West (Northern California) Region",
        'ami': "ami-01aba244"
    },
    'us-west-2': {
        'name': "US West (Oregon) Region",
        'ami': "ami-1189c921"
    },
}


def valid_region(region):
    if region in REGIONS.keys():
        return region
    else:
        raise TypeError("%s is not a valid region" % region)


def all_regions(instances):
    regions = []
    for instance in instances:
        if instance.region not in regions:
            regions.append(instance.region)
    return regions
