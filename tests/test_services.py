from skipper.services import (
    Service, check_already_uploaded, get_next_version, image_id_from_events)
from skipper.builder import Repo

import pytest
import mock


def test_init():
    service = Service(
        name="test",
        build=".",
        repo="cameronmaske/flask-web",
        loadbalance=["80:80"],
        scale=10
    )

    assert service.name == "test"
    assert service.build == "."
    assert service.loadbalance == {80: 80}
    assert service.scale == 10
    assert isinstance(service.repo, Repo)
    assert service.repo.name == "cameronmaske/flask-web"
    assert service.repo.registry == "index.docker.io"


def test_repo_required():
    with pytest.raises(TypeError):
        Service(name="test")


def test_service_repo(service, repo):
    service.repo = "cameronmaske/node-web"
    assert isinstance(service.repo, Repo)
    assert service.repo.name == "cameronmaske/node-web"
    assert service.repo.registry == "index.docker.io"

    service.repo = {
        'name': "cameronmaske/django-web",
        'registry': "private.index.docker.io"
    }
    assert isinstance(service.repo, Repo)
    assert service.repo.name == "cameronmaske/django-web"
    assert service.repo.registry == "private.index.docker.io"

    service.repo = repo
    assert service.repo == repo

    with pytest.raises(TypeError):
        service.repo = {
            'registry': "private.index.docker.io"
        }


def test_build_image(service):
    service.build = "."
    with mock.patch('docker.Client') as client:
        client().build.return_value = [
            '{"stream":"Step 0 : FROM ubuntu"}',
            '{"stream":"Step 6 : CMD echo hello"}',
            '{"stream":"Successfully built fdb2b414110f"}'
        ]
        image_id = service.build_image()
        assert image_id == 'fdb2b414110f'


def test_build_image_no_build(service):
    service.build = None
    with pytest.raises(Exception):
        service.build_image()


def test_upload(repo, service):
    repo = mock.MagicMock(spec=repo)
    service.repo = repo
    service.repo.get_tags.return_value = [
        {
            'layer': '1',
            'name': 'latest'
        },
        {
            'layer': '2',
            'name': 'v1'
        },
    ]
    service.repo.upload.return_value = None
    service.upload('3')
    service.repo.upload.assert_called_with('3', 'v2')
    assert service.repo.tag == 'v2'


def test_upload_already_uploaded(repo, service):
    repo = mock.MagicMock(spec=repo)
    service.repo = repo
    service.repo.get_tags.return_value = [
        {
            'layer': '1',
            'name': 'latest'
        },
        {
            'layer': '2',
            'name': 'v1'
        },
    ]
    service.repo.upload.return_value = None
    service.upload('2')
    assert not service.repo.upload.called
    assert service.repo.tag == 'v1'


@pytest.fixture()
def tags():
    return [
        {
            'layer': '1',
            'name': 'latest'
        },
        {
            'layer': '2',
            'name': 'v1'
        },
        {
            'layer': '3',
            'name': 'foo'
        },
        {
            'layer': '4',
            'name': 'v2'
        }
    ]


def test_check_already_uploaded(tags, project):
    assert check_already_uploaded('2', tags) == 'v1'
    assert check_already_uploaded('5', tags) is None


def test_get_next_version(tags):
    version = get_next_version(tags)
    assert version == 3


def test_image_id_from_events():
    events = ['foo', 'Successfully built fdb2b414110f', 'bar']
    image_id = image_id_from_events(events)
    assert image_id == "fdb2b414110f"
