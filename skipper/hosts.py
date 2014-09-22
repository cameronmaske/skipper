import click
import os


def get_host(host):
    """
    Based on the host agrumement passed in, determine which host to pass back.
    """
    # WIP: Only aws for now!
    from skipper.aws.host import host
    return host


class BaseHost(object):
    def check_file(self, message):
        exists = False
        while not exists:
            path = os.path.expanduser(click.prompt(message))
            exists = os.path.isfile(path)
            if not exists:
                click.echo("Sorry, that doesn't appear to be a valid file.")
        return path

    def get_keys_paths(self):
        public = self.creds['SSH'].get('PUBLIC_KEY')
        if not public:
            public = self.check_file('Please enter the path to a SSH public key')
            self.creds['SSH']['PUBLIC_KEY'] = public
            self.creds.save()

        private = self.creds['SSH'].get('PRIVATE_KEY')
        if not private:
            private = self.check_file('Please enter the path to a SSH private key')
            self.creds['SSH']['PRIVATE_KEY'] = private
            self.creds.save()

        return {
            "private": private,
            "public": public
        }

    def get_etcd_token(self):
        if not self.creds['COREOS']['ETCD_TOKEN']:
            click.echo('\nNo token set for your etcd cluster.')
            self.creds['COREOS']['ETCD_TOKEN'] = click.prompt(
                'Please visit https://discovery.etcd.io/new to generate a new'
                ' one, or enter your existing one'
            )
            self.creds.save()
            click.echo('\n')
        return self.creds['COREOS']['ETCD_TOKEN']
