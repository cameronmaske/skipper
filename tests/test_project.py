import yaml

from skipper.project import Project


def test_parse_config():
    skipper_yml = """
name: demo
instances:
  web:
    size: m1.small
    loadbalance:
      - "80:80"
    scale: 2
    regions:
      - us-east-1
      - us-west-1
services:
  web:
    build: .
    loadbalance:
      - "80:5000"
    scale: 2
    test: "python manage.py tests"
    registry:
      name: cameronmaske/flask-web
    """

    config = yaml.load(skipper_yml)
    project = Project()
    project.from_config(config)

    assert project.name == "demo"
    assert len(project.services) == 1
    assert len(project.instances) == 2
