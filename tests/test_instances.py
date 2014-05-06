from skipper.instances import Instance


def test_create():
    details = {
        'region': "eu-west-1",
        'size': "m1.small"
    }

    instance = Instance(name="web", count=1, **details)
    assert instance.name == "web"
    assert instance.count == 1
    assert instance.uuid == "web_1"
    assert instance.region == "eu-west-1"
    assert instance.size == "m1.small"
