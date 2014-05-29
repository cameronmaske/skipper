import click
from utils import contains_keys


def get_host(host):
    """
    Based on the host agrumement passed in, determine which host to pass back.
    """
    # WIP: Only aws for now!
    from skipper.aws.host import host
    return host


class BaseHost(object):
    def check_requirements(self):
        field = self.requirements['field']
        if not contains_keys(self.requirements['keys'], self.creds[field]):
            click.utils.echo(self.requirements['message'])
            for key, message in self.requirements['keys'].items():
                self.creds[field][key] = click.prompt(message)
                self.creds.save()
