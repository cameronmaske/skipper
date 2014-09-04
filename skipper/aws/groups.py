from __future__ import unicode_literals


class Group(object):
    def __repr__(self):
        return '(Group: %s)' % self.name

    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.size = kwargs.get('size')
        self.scale = kwargs.get('scale', 1)
        self.region = kwargs.get('region', "us-east-1")
        self.services = kwargs.get('services', [])
        self.ports = kwargs.get("ports", {
            "public": {}
        })

    def details(self):
        return {
            "size": self.size,
            "scale": self.scale,
            "region": self.region,
            "ports": self.ports
        }
