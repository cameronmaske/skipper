from texttable import Texttable


def instance_table(instances, width):
    table = Texttable(max_width=width)
    headers = ["uuid", "state", "ip", "size", "group", "scale"]
    rows = []
    for instance in instances:
        rows.append([
            instance['uuid'],
            instance['state'],
            instance['ip'],
            instance['size'],
            instance['group'],
            instance['scale']
        ])
    table.set_chars(['-', '|', '+', '-'])
    table.add_rows([headers] + rows)
    return table.draw()
