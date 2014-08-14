def parse_port(ports_string):
    """
    Turns "80:80" -> {80: 80}
    """
    guest, host = ports_string.split(':')
    ports = {}
    ports[int(guest)] = int(host)
    return ports


def parse_ports(ports):
    clean_ports = {}
    for port in ports:
        if type(port) == str:
            try:
                port = parse_port(port)
            except ValueError:
                port = {int(port): None}
        clean_ports.update(port)
    return clean_ports
