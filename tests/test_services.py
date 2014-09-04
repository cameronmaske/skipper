from skipper.services import (
    Service, image_id_from_events, split_tags_and_services, outdated_images)
from skipper.exceptions import (
    ServiceException, RepoNotFound, RepoNoPermission)

import httpretty
import pytest
import mock


def test_init():
    service = Service(
        name="test",
        repo={
            "name": "cameronmaske/flask-web"
        },
        build=".",
        ports=["80:80"],
        scale=10
    )

    assert service.name == "test"
    assert service.build == "."
    assert service.ports == {80: 80}
    assert service.scale == 10
    assert service.repo == {
        'name': "cameronmaske/flask-web",
    }


def test_build_image(service):
    service.build = "."
    service.client.build.return_value = [
        '{"stream":"Step 0 : FROM ubuntu"}',
        '{"stream":"Step 6 : CMD echo hello"}',
        '{"stream":"Successfully built fdb2b414110f"}'
    ]
    image_id = service.build_image()
    assert image_id == 'fdb2b414110f'


def test_build_image_no_build(service):
    service.build = None
    with pytest.raises(ServiceException):
        service.build_image()


def test_clean_images(service):
    service.client.images.return_value = [
        {
            'RepoTags': ["service:v2"],
            'Created': 100,
        },
        {
            'RepoTags': ["service:v1"],
            'Created': 50,
        },
    ]

    service.clean_images(cutoff=1)
    service.client.remove_image.assert_called_with(
        "service:v1", force=True)


def test_get_remote_tags(service):
    httpretty.enable()
    httpretty.register_uri(
        httpretty.GET, "https://index.docker.io/v1/repositories/cameronmaske/flask-web/tags",
        body='[{"layer": "66967a62", "name": "v1"}]',
        content_type="application/json"
    )
    tags = service.get_remote_tags()
    assert tags == [{"layer": "66967a62", "name": "v1"}]


def test_get_remote_tags_404(service):
    httpretty.enable()
    httpretty.register_uri(
        httpretty.GET, "https://index.docker.io/v1/repositories/cameronmaske/flask-web/tags",
        body='Not found!',
        status=404
    )

    with pytest.raises(RepoNotFound):
        service.get_remote_tags()


def test_push(service):
    service.client.push.return_value = [
        '{"status":"The push refers to a repository [cameronmaske/flask-web] (len: 12)"}',
        '{"status":"Image 4d26dd3ebc1c already pushed, skipping"}',
        '{"status":"Pushing tag for rev [12eacdfb9310] on {https://registry-1.docker.io/v1/repositories/cameronmaske/flask-web/tags/v6}"}'
    ]
    service.push(tag="v1")
    service.client.push.assert_called_with(
        "cameronmaske/flask-web", tag="v1", stream=True
    )


def test_push_403_error(service):
    service.client.push.return_value = [
        '{"errorDetail":{"message":"Error: Status 403 trying to push repository: Access Denied: Not allowed to create Repo at given location"},"error":"Error: Status 403 trying to push repository: Access Denied: Not allowed to create Repo at given location"}'
    ]
    with pytest.raises(RepoNoPermission):
        service.push(tag="v1")


def test_push_401_error(service):
    service.client.push.return_value = [
        '{"errorDetail":{"message":"Error: Status 401 trying to push repository: Access Denied: Not allowed to create Repo at given location"},"error":"Error: Status 401 trying to push repository: Access Denied: Not allowed to create Repo at given location"}'
    ]
    with pytest.raises(RepoNoPermission):
        service.push(tag="v1")


def test_create_tag(service):
    service.build_image = mock.Mock(return_value="abc")
    image_id = service.create_tag(tag="v1")
    service.client.tag.assert_called_with(
        image="abc", repository="cameronmaske/flask-web", tag="v1"
    )
    assert image_id == "abc"


def test_outdated_images():
    images = [
        {
            'RepoTags': ["service:v4"],
            'Created': 150,
        },
        {
            'RepoTags': ["service:v2", "service:v3"],
            'Created': 100,
        },
        {
            'RepoTags': ["service:v1"],
            'Created': 50,
        },
    ]
    outdated = outdated_images(images, cutoff=2)
    assert outdated == ["service:v1", "service:v2"]


def test_image_id_from_events():
    events = ['foo', 'Successfully built fdb2b414110f', 'bar']
    image_id = image_id_from_events(events)
    assert image_id == "fdb2b414110f"


def test_split_tags_and_services():
    example = ["web:v1", "celery"]
    result = split_tags_and_services(example)
    assert result == {
        "web": "v1",
        "celery": None
    }
