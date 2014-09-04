import pytest
import mock

from skipper.aws.instances import Instance


@pytest.fixture()
def aws_instance():
    instance = Instance(
        host=mock.MagicMock(),
        uuid="uuid",
        project_name="project_name",
        boto_instance=mock.MagicMock())
    return instance


def test_instance_valid_region(aws_instance):
    aws_instance.valid_region('us-east-1')
    assert aws_instance.region == 'us-east-1'


def test_instance_invalid_region(aws_instance):
    with pytest.raises(TypeError):
        aws_instance.valid_region('space-station-7')


def test_instance_valid_size(aws_instance):
    aws_instance.valid_size('t1.micro')
    assert aws_instance.size == 't1.micro'


def test_instance_invalid_size(aws_instance):
    with pytest.raises(TypeError):
        aws_instance.valid_size('t9.gigantic')
