from __future__ import unicode_literals


class Service(object):
    def __repr__(self):
        return '(Service: %s)' % self.name

    def __init__(self, name, **kwargs):
        self.name = name
        self.path = kwargs.get('build')
        self.registry = kwargs.get('registry')

    def build(self):
        raise NotImplementedError()


