from skipper.loadbalancer.helpers import parse_port


def test_parse_ports():
    port_string = "80:8000"
    port = parse_port(port_string)
    assert port == {80: 8000}
