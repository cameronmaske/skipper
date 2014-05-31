from skipper.builder import Repo, RepoNotFound, RepoNoPermission

import httpretty
import pytest
import mock


def test_init():
    repo = Repo(
        name="cameronmaske/flask-web",
        registry="private.index.docker.io",
        tag="master"
    )
    assert repo.name == "cameronmaske/flask-web"
    assert repo.registry == "private.index.docker.io"
    assert repo.tag == "master"


def test_get_tags(repo):
    httpretty.enable()
    httpretty.register_uri(
        httpretty.GET, "https://index.docker.io/v1/repositories/cameronmaske/flask-web/tags",
        body='[{"layer": "66967a62", "name": "v1"}]',
        content_type="application/json"
    )
    tags = repo.get_tags()
    assert tags == [{"layer": "66967a62", "name": "v1"}]


def test_get_tags_404(repo):
    httpretty.enable()
    httpretty.register_uri(
        httpretty.GET, "https://index.docker.io/v1/repositories/cameronmaske/flask-web/tags",
        body='Not found!',
        status=404
    )

    with pytest.raises(RepoNotFound):
        repo.get_tags()


def test_upload(repo):
    with mock.patch('docker.Client') as client:
        client().push.return_value = [
            '{"status":"The push refers to a repository [cameronmaske/flask-web] (len: 12)"}',
            '{"status":"Image 4d26dd3ebc1c already pushed, skipping"}',
            '{"status":"Pushing tag for rev [12eacdfb9310] on {https://registry-1.docker.io/v1/repositories/cameronmaske/flask-web/tags/v6}"}'
        ]
        repo.upload('1', 'v1')
        client().tag.assert_called_with(image='1', repository=repo.name, tag='v1')
        client().push.assert_called_with(repo.name, stream=True)


def test_upload_403_error(repo):
    with mock.patch('docker.Client') as client:
        client().push.return_value = [
            '{"errorDetail":{"message":"Error: Status 403 trying to push repository: Access Denied: Not allowed to create Repo at given location"},"error":"Error: Status 403 trying to push repository: Access Denied: Not allowed to create Repo at given location"}'
        ]
        with pytest.raises(RepoNoPermission):
            repo.upload('1', 'v1')


def test_upload_401_error(repo):
    with mock.patch('docker.Client') as client:
        client().push.return_value = [
            '{"errorDetail":{"message":"Error: Status 401 trying to push repository: Access Denied: Not allowed to create Repo at given location"},"error":"Error: Status 401 trying to push repository: Access Denied: Not allowed to create Repo at given location"}'
        ]
        with pytest.raises(RepoNoPermission):
            repo.upload('1', 'v1')
