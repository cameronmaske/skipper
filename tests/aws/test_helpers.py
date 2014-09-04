from skipper.aws.helpers import outdated_rules, find_instance, find_machine_by_ip

import mock


def test_find_instance():
    instance1 = mock.Mock(private_ip="1.0.0.1")
    instance2 = mock.Mock(private_ip="1.0.0.2")
    instances = [instance1, instance2]
    machines = [
        {"primaryIP": "1.0.0.1", "id": "1"},
        {"primaryIP": "1.0.0.2", "id": "2"}
    ]
    found = find_instance(instances, machines, "2")
    assert found == instance2


def test_outdated_rules():
    existing = [
        mock.Mock(
            ip_protocol="tcp",
            from_port=81,
            to_port=81,
            grants=["1.0.0.1"]
        ),
        mock.Mock(
            ip_protocol="tcp",
            from_port=80,
            to_port=80,
            grants=["1.0.0.1"]
        )
    ]
    desired = [
        {
            "ip_protocol": "tcp",
            "from_port": 80,
            "to_port": 80,
            "to_ip":["1.0.0.1"]
        }
    ]
    expected = [
        {
            "ip_protocol": "tcp",
            "from_port": 81,
            "to_port": 81,
            "to_ip":["1.0.0.1"]
        }
    ]
    outdated = outdated_rules(existing, desired)
    assert expected == outdated


def test_find_machine_by_ip():
    machines = [
        {"primaryIP": "1.0.0.1", "id": "1"},
        {"primaryIP": "1.0.0.2", "id": "2"}
    ]
    machine_id = find_machine_by_ip(machines, ip="1.0.0.2")
    assert machine_id == {"primaryIP": "1.0.0.2", "id": "2"}
