import json
import click

from utils import contains_keys


class BaseConfig(dict):
    def __init__(self, *args, **kwargs):
        super(BaseConfig, self).__init__(*args, **kwargs)
        self.update(self.retrieve())

    def __setitem__(self, *args, **kwargs):
        super(BaseConfig, self).__setitem__(*args, **kwargs)
        self.save()

    def __delitem__(self, *args, **kwargs):
        super(BaseConfig, self).__delitem__(*args, **kwargs)
        self.save()

    def retrieve(self):
        return {}

    def save(self):
        pass


class Config(BaseConfig):
    def retrieve(self):
        try:
            with open('skipper.json', 'r') as f:
                try:
                    return json.load(f)
                except ValueError:
                    return {}
        except IOError:
            return {}

    def save(self):
        with open('skipper.json', 'w+') as f:
            f.write(json.dumps(self, indent=2))


def get_config(requirements):
    config = Config()

    if not contains_keys(requirements['keys'], config):
        click.utils.echo(requirements['message'])
        for key, message in requirements['keys'].items():
            config[key] = click.prompt(message)
    return config
