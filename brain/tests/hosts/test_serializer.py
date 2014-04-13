from django.test import TestCase


from hosts.api.serializer import HostSerializer
from hosts.models import Host


class HostSerializerTestCase(TestCase):
    def test_retrieve(self):
        host = Host(
            id=1,
            name='Awesome Host',
            host='127.0.0.1',
            port=8000,
            ssh_setup=False)

        serializer = HostSerializer(host)

        expected = {
            'id': 1,
            'name': 'Awesome Host',
            'host': '127.0.0.1',
            'port': 8000,
            'ssh_setup': False}

        self.assertDictEqual(serializer.data, expected)

    def test_create(self):
        content = {
            'name': 'My first host',
            'host': '127.0.0.1',
            'port': 8000,
        }

        serializer = HostSerializer(data=content)
        self.assertEqual(serializer.is_valid(), True)
        host = serializer.save()
        self.assertEqual(host.name, content['name'])
        self.assertEqual(host.host, content['host'])
        self.assertEqual(host.port, content['port'])

