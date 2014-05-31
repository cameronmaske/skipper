from skipper.project import Project, NoSuchService
from skipper.builder import Repo
from skipper.services import Service

import pytest


def test_init(host):
    project = Project(name="test", host=host)
    assert project.name == "test"
    assert project.host == host
    assert project.services == []
    assert repr(project) == "Project (test)"


def test_make_service(project):
    service = project.make_service(**{
        'name': 'web',
        'build': '.',
        'loadbalance': ["80:5000"],
        'scale': 2,
        'repo': {
            'name': 'cameronmaske/flask-web'
        }
    })

    assert isinstance(service, Service)
    assert service.name == 'web'
    assert service.build == '.'
    assert service.loadbalance == [{80: 5000}]
    assert service.scale == 2
    assert isinstance(service.repo, Repo)
    assert service.repo.name == "cameronmaske/flask-web"
    assert service.repo.registry == "index.docker.io"


def test_get_service(project):
    service1 = Service(name="service1", repo="cameronmaske/flask-web")
    service2 = Service(name="service2", repo="cameronmaske/node-web")
    project.services = [service1, service2]

    got = project.get_service("service1")
    assert got == service1

    with pytest.raises(NoSuchService):
        project.get_service("no-service")


def test_filter_services(project):
    service1 = Service(name="service1", repo="cameronmaske/flask-web")
    service2 = Service(name="service2", repo="cameronmaske/node-web")
    project.services = [service1, service2]

    found = project.filter_services(["service1", "service2"])
    assert found == [service1, service2]

    found = project.filter_services(["service1"])
    assert found == [service1]

    found = project.filter_services([])
    assert found == [service1, service2]

    with pytest.raises(NoSuchService):
        project.filter_services(["no-service"])

