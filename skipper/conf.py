import yaml


def get_conf():
    conf = yaml.load(open('skipper.yml'))
    return conf
