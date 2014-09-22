from skipper.aws.host import Host

import mock
import pytest


@pytest.fixture
def aws_host(project):
    ec2 = mock.MagicMock()
    host = Host(
        creds={}, project=project)
    host._ec2 = ec2
    return host


def test_make_group(aws_host):
    group = aws_host.make_group(
        name="web",
        size="t1.micro",
        scale=1,
        region="us-east-1",
        ports={
            "public": [80]
        }
    )

    assert group.name == "web"
    assert group.size == "t1.micro"
    assert group.scale == 1
    assert group.region == "us-east-1"
    assert group.ports == {
        "public": [80]
    }


def test_make_group_invalid_port(aws_host):
    with pytest.raises(ValueError):
        aws_host.make_group(
            name="web",
            size="t1.micro",
            scale=1,
            region="us-east-1",
            ports={
                "public": ["abc"]
            }
        )