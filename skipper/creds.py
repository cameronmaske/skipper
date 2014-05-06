import json
import click

from utils import contains_keys


class NestedDict(dict):
    """
    A dictonary that allows 'autovivification'.
    Allows you to set undefined (nested) values.


    >> foo = NestedDict()
    >> foo['d']['e']
    {}
    >> foo['a']['b'][c] = 1
    >> foo
    {'a': {'b':{'c': 1}}}
    """

    def __missing__(self, key):
        value = self[key] = NestedDict()
        return value


class Creds(NestedDict):
    """
    Dictonary to store various credential details (e.g. secret keys,
    private keys, etc)
    """
    def __init__(self, storage, *args, **kwargs):
        super(Creds, self).__init__(*args, **kwargs)
        self.storage = storage
        self.update(self.storage.retrieve())

    def __setitem__(self, *args, **kwargs):
        super(Creds, self).__setitem__(*args, **kwargs)
        self.storage.save(self)

    def __delitem__(self, *args, **kwargs):
        super(Creds, self).__delitem__(*args, **kwargs)
        self.storage.save(self)


class JSONStorage(object):
    """
    Stores a config in a json format in a .skippercfg file.
    """
    def retrieve(self):
        try:
            with open('.skippercfg', 'r') as f:
                try:
                    return json.load(f)
                except ValueError:
                    return {}
        except IOError:
            return {}

    def save(self, config):
        with open('.skippercfg', 'w+') as f:
            f.write(json.dumps(config, indent=2))


creds = Creds(storage=JSONStorage())


def get_creds(requirements):
    if not contains_keys(requirements['keys'], creds):
        click.utils.echo(requirements['message'])
        for key, message in requirements['keys'].items():
            creds[key] = click.prompt(message)
    return creds
