import re


def get_subset(a, keys):
    return dict((k, a[k]) for k in keys if k in a)


def find(array, properties):
    keys = properties.keys()
    for a in array:
        dict_a = a
        if hasattr(a, '__dict__'):
            dict_a = a.__dict__
        subset = get_subset(dict_a, keys)
        if subset == properties:
            return a
    return None


def contains_keys(a, b):
    return set(a.keys()).issubset(b.keys())


def get_index(x, index):
    """
    Get the element at the index of the list or return None
    >>> example = [1, 2]
    >>> get_index(example, 1)
    1
    >>> get_index(example, 7)
    None
    """
    if len(x) > index:
        return x[index]


def extract_version(event):
    """
    Parses the output from docker --version for the version, e.g.

    >>> extract_version("Docker version 0.11.1, build fb99f99")
    "0.11.1"
    """
    match = re.search(r'Docker version ([0-9\.]+),', event)
    if match:
        version = match.group(1)
    return version
