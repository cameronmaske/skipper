import pytest
from skipper.aws.instances import Instance
from skipper.exceptions import ConfigurationException


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
