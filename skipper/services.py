def generate_services(configuration):
    """
    Turns...
    {
        'web': {
            'build': '.'
            'test': 'python manage.py tests',
            'scale': 2,
            'loadbalance': ['80:5000'],
            'registry': {
                'name': 'cameronmaske/flask-web'
            },
        }
    }

    Into...
    [Service()]
    """
    services = []
    for name, details in configuration.items():
        services += parse_services(name, details)
    return services


def parse_services(name, details):
    services = [Service(name, **details)]
    return services


class Service(object):
    def __repr__(self):
        return '(Service: %s)' % self.name

    def __init__(self, name, **kwargs):
        self.name = name
