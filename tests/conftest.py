from skipper.services import Service
from skipper.project import Project

from docker import Client
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
def service():
    service = Service(
        name="service",
        repo={
            'name': "cameronmaske/flask-web",
        })
    service.client = mock.Mock(spec_set=Client)
    return service


@pytest.fixture
def services(repo):
    service1 = Service(
        name="service1",
        repo={
            'name': "cameronmaske/flask-web"
        })
    service2 = Service(
        name="service2",
        repo={
            'name': "cameronmaske/node-web"
        })
    return [service1, service2]
