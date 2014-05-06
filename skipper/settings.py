import yaml


def get_settings():
    settings = yaml.load(open('skipper.yml'))
    return settings
