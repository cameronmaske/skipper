import os
import docker


def _docker():
    """
    Cached Docker client.
    Approach taken from https://github.com/andreasjansson/head-in-the-clouds/blob/master/headintheclouds/ec2.py#L327
    """
    if not hasattr(_docker, 'client'):
        _docker.client = docker.Client(os.environ.get('DOCKER_HOST'))
    return _docker.client
