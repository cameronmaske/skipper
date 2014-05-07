import json
import click


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
        with open('skipper.json', 'r') as f:
            try:
                return json.load(f)
            except ValueError:
                return {}

    def save(self):
        with open('skipper.json', 'w+') as f:
            f.write(json.dumps(self, indent=2))


def get_config():
    config = Config()
    if not config['ACCESS_KEY'] or not config['SECRET_KEY']:
        click.utils.echo("""As this is your first time running skipper, we need to store your some AWS Security Credentials.
Please visit https://console.aws.amazon.com/iam/home?#security_credential
Under Access Keys, click Create New Access Key.""")
        config['ACCESS_KEY'] = click.prompt("Enter your Access Key ID")
        config['SECRET_KEY'] = click.prompt("Enter your Secret Access Key")
    return config
