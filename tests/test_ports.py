from skipper.ports import (
    parse_port, parse_ports_dict, parse_ports_list)

import pytest


def test_parse_ports():
    port = parse_port("80:8000")
    assert port == {80: 8000}


def test_parse_ports_dict():
    ports = parse_ports_dict(["80:5000", "90"])
    assert ports == {
        80: 5000,
        90: None
    }


def test_parse_ports_list():
    ports = parse_ports_list(["80"])
    assert ports == [80]


def test_parse_ports_list_value_error():
    with pytest.raises(ValueError):
        parse_ports_list(["80:80"])
