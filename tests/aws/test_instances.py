import pytest
from skipper.aws.instances import (
    Instance, parse_settings, instances_to_create, instances_to_remove)
from skipper.exceptions import ConfigurationException


def test_parse_settings():
    settings = {
        'web': {
            'size': 't1.micro',
            'scale': 2,
            'regions': ['us-east-1', 'us-west-1'],
            'loadbalance': ['80:80']
        }
    }

    instances = parse_settings(settings)

    expected = [
        {
            'name': 'web',
            'size': 't1.micro',
            'region': 'us-east-1',
            'loadbalance': [{80: 80}],
            'scale': 1,
        },
        {
            'name': 'web',
            'size': 't1.micro',
            'region': 'us-west-1',
            'loadbalance': [{80: 80}],
            'scale': 1,
        },
        {
            'name': 'web',
            'size': 't1.micro',
            'region': 'us-east-1',
            'loadbalance': [{80: 80}],
            'scale': 2,
        },
        {
            'name': 'web',
            'size': 't1.micro',
            'region': 'us-west-1',
            'loadbalance': [{80: 80}],
            'scale': 2,
        }
    ]

    assert instances == expected


def test_instance_valid_region():
    instance = Instance(name="test")
    instance.valid_region('us-east-1')
    assert instance.region == 'us-east-1'


def test_instance_invalid_region():
    instance = Instance(name="test")

    with pytest.raises(ConfigurationException):
        instance.valid_region('space-station-7')


def test_instance_valid_size():
    instance = Instance(name="test")
    instance.valid_size('t1.micro')
    assert instance.size == 't1.micro'


def test_instance_invalid_size():
    instance = Instance(name="test")

    with pytest.raises(ConfigurationException):
        instance.valid_size('t9.gigantic')

from boto.ec2.instance import Instance as BotoInstance


def test_instances_to_create():
    existing_instance = BotoInstance()
    existing_instance.tags = {
        'skipper': 'aye-aye',
        'uuid': 'web_1_us-east-1',
        'project': 'test',
    }

    existing_instances = [existing_instance]

    instance1 = Instance(name="web", scale=1, size="t1.micro", region="us-east-1")
    instance2 = Instance(name="db", scale=1, size="t1.micro", region="us-east-1")
    instances = [instance1, instance2]

    to_create = instances_to_create(instances, existing_instances)

    assert len(to_create) == 1
    assert to_create[0] == instance2


def test_instances_to_remove():
    existing_instance = BotoInstance()
    existing_instance.tags = {
        'skipper': 'aye-aye',
        'uuid': 'web_1_us-east-1',
        'project': 'test',
    }

    redudant_instance = BotoInstance()
    redudant_instance.tags = {
        'skipper': 'aye-aye',
        'uuid': 'web_2_us-east-1',
        'project': 'test',
    }

    existing_instances = [existing_instance, redudant_instance]

    instance = Instance(name="web", scale=1, size="t1.micro", region="us-east-1")
    instances = [instance]

    to_remove = instances_to_remove(instances, existing_instances)

    assert len(to_remove) == 1
    assert to_remove[0] == redudant_instance
