from boto import ec2, exception
from skipper.cli import logger


class Host(object):
    def __init__(self, config, project=None):
        self.attach_config(config)
        if project:
            self.attach_project(project)

    def attach_config(self, config):
        self.config = config
        self.conn = ec2.connection.EC2Connection(
            config['ACCESS_KEY'], config['SECRET_KEY'])

    def attach_project(self, project):
        self.project = project

    def setup(self):
        # If we don't have a private key stored, should go ahead and generate
        # a new one. If one already exists, raise an error.
        key_name = "skipper_%s" % self.project.name

        if not self.config['PRIVATE_KEY']:
            try:
                key = self.conn.get_all_key_pairs(keynames=[key_name])[0]
            except exception.EC2ResponseError as e:
                if e.code == 'InvalidKeyPair.NotFound':
                    logger.info("""No existing EC2 Key Pair can be found for %s.
                        A new one will be generated and stored in .skippercfg""" % self.project.name)
                    key = self.conn.create_key_pair(key_name)
                else:
                    raise e

            if not key.material:
                logger.error("""
                    An EC2 Key pair already exists for this project.
                    Please add the private key to .skippercfg""")
            else:
                logger.info("Succesfully generated a new EC2 Key Pair.")
                self.config['PRIVATE_KEY'] = key.material

