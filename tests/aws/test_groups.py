from skipper.aws.groups import Group


def test_group():
    group = Group(
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
