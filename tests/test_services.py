from skipper.services import highest_tag_version


def test_highest_tag_version():
    tags = {
        'latest': 'bla',
        'v1': 'bla',
        'v2': 'bla',
        '8000': 'bla',
        'foo': 'bla',
    }
    highest = highest_tag_version(tags)
    assert highest == 2
