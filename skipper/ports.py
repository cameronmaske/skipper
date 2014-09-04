def parse_port(ports_string):
    """
    Turns "80:80" -> {80: 80}
    """
    guest, host = ports_string.split(':')
    ports = {}
    ports[int(guest)] = int(host)
    return ports


def parse_ports_dict(ports):
    """
    Turns a list of string ports into a dictonary of ports
    with the key and value being outside and inside the container
    respectively.

    Example:

    ["80:5000", "90"]

    into...

    {
        80: 5000
        90: None
    }
    """
    clean_ports = {}
    for port in ports:
        if type(port) == str:
            try:
                port = parse_port(port)
            except ValueError:
                port = {int(port): None}
        clean_ports.update(port)
    return clean_ports


def parse_ports_list(ports):
    """
    Turns a list of port strings into a list of ports int.

    Example:

    ["80", "9000"]

    into...

    [80, 9200]
    """
    clean_ports = []
    for port in ports:
        try:
            clean_ports.append(int(port))
        except ValueError:
            if ":" in port:
                hint = """{} does not appear to be a valid port.
                Format should only include a single port to expose,
                e.g. 80 not 80:80""".format(port)
            else:
                hint = "{} does not appear to be a valid port".format(port)
            raise ValueError(hint)
    return clean_ports
