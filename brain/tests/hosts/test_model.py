from django.test import TestCase

from hosts.model import Host


class HostModelTestCase(TestCase):
    def test_env(self):
        host = Host(
            name='My first host',
            host='127.0.0.1',
            port=8000)

        self.assertEquals(host.env(), {
            'hostname': '127.0.0.1',
            'port': 8000
        })
