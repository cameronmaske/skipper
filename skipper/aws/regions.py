# All possible regions of EC2 instances.
# http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html
# https://cloud-images.ubuntu.com/locator/ec2/a
# Includes the humanize name of the region and the AMI (64-bit EBS)

REGIONS = {
    'ap-northeast-1': {
        'name': "Asia Pacific (Tokyo) Region",
        'ami': "ami-3f32ac3e"
    },
    'ap-southeast-1': {
        'name': "Asia Pacific (Singapore) Region",
        'ami': "ami-b84e04ea"
    },
    'ap-southeast-2': {
        'name': "Asia Pacific (Sydney) Region",
        'ami': "ami-3d128f07"
    },
    'eu-west-1': {
        'name': "EU (Ireland) Region",
        'ami': "ami-af7abed8"
    },
    'sa-east-1': {
        'name': "South America (Sao Paulo) Region",
        'ami': "ami-35258228"
    },
    'us-east-1': {
        'name': "US East (Northern Virginia) Region",
        'ami': "ami-a73264ce"
    },
    'us-west-1': {
        'name': "US West (Northern California) Region",
        'ami': "ami-acf9cde9"
    },
    'us-west-2': {
        'name': "US West (Oregon) Region",
        'ami': "ami-6aad335a"
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
