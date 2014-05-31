def parse_port(ports_string):
    """
    Turns "80:80" -> {80: 80}
    """
    guest, host = ports_string.split(':')
    ports = {}
    ports[int(guest)] = int(host)
    return ports
