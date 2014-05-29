from skipper.services import Service
from skipper.project import Project
from skipper.builder import Repo

import pytest
import mock


@pytest.fixture
def host():
    return mock.MagicMock()


@pytest.fixture
def project(host):
    project = Project(name="test", host=host)
    return project


@pytest.fixture
def repo():
    repo = Repo(
        name="cameronmaske/flask-web",
        registry="index.docker.io"
    )
    return repo


@pytest.fixture
def service(repo):
    service = Service(name="service", repo=repo)
    return service


@pytest.fixture
def services(repo):
    service1 = Service(name="service1", repo="cameronmaske/flask-web")
    service2 = Service(name="service2", repo="cameronmaske/node-web")
    return [service1, service2]
