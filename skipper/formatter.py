from texttable import Texttable


def instance_table(instances, width):
    table = Texttable(max_width=width)
    headers = ['uuid', 'state', 'ip', 'size', 'group', 'scale', 'region']
    rows = []
    for instance in instances:
        rows.append([
            instance['uuid'],
            instance['state'],
            instance['ip'],
            instance['size'],
            instance['group'],
            instance['scale'],
            instance['region']
        ])
    table.set_chars(['-', '|', '+', '-'])
    table.add_rows([headers] + rows)
    return table.draw()


def service_table(services, width):
    table = Texttable(max_width=width)
    headers = ['uuid', 'state', 'instance', 'ip', 'service', 'scale']
    rows = []
    for service in services:
        rows.append([
            service['uuid'],
            service['state'],
            service['instance'],
            service['ip'],
            service['service'],
            service['scale']
        ])
    table.set_chars(['-', '|', '+', '-'])
    table.add_rows([headers] + rows)
    return table.draw()
