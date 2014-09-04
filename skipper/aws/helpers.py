def find_instance(instances, machines, machine_id):
    """
    Figures out which instance belongs to a list of fleet machines based on
    a machine_id.
    """
    for instance in instances:
        machine = find_machine_by_ip(machines, instance.private_ip)
        if machine:
            if machine["id"] == machine_id:
                return instance


def outdated_rules(existing, desired):
    """
    Determines which rules are no longer needed, based comparing an existing rule
    set to the desired rules.
    """
    outdated = []
    for rule in existing:
        normalized = {
            "ip_protocol": rule.ip_protocol,
            "from_port": rule.from_port,
            "to_port": rule.to_port,
            "to_ip": [str(ip) for ip in rule.grants]
        }
        if normalized not in desired:
            outdated.append(normalized)
    return outdated


def find_machine_by_ip(machines, ip):
    """
    From a list of machines, returns the matching machine id.

    Example:

    >>> machines = [
        {
            "id": "abc",
            "primaryIP": "1.1.1.1"
        },
        {
            "id": "xyz",
            "primaryIP": "2.2.2.2"
        }
    ]
    >>> find_machine_by_ip(machine_id, "2.2.2.2")
    "xyz"
    """
    for machine in machines:
        if machine['primaryIP'] == ip:
            return machine
