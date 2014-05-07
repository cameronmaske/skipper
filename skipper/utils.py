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
