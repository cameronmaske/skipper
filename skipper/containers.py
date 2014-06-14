from fig.container import Container as FigContainer


def clean_port(dirty):
    clean = dirty.replace('/tcp', '')
    return int(clean)


class Container(FigContainer):

    @property
    def repo(self):
        name, tag = self.image.split(':', 1)
        return {
            'name': name,
            'tag': tag,
        }

    @property
    def ports(self):
        self.inspect_if_not_inspected()
        ports = {}
        if not self.dictionary['NetworkSettings']['Ports']:
            return ports
        for private, public in list(self.dictionary['NetworkSettings']['Ports'].items()):
            if public:
                ports[clean_port(private)] = clean_port(public[0]['HostPort'])
        return ports

    @property
    def params(self):
        (name, version, scale) = self.name.split("_", 3)
        return {
            'name': name,
            'version': version,
            'scale': scale
        }

