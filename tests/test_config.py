from skipper.config import BaseConfig


def test_config():
    config = BaseConfig()
    config['access_key'] = 'foo'
    assert config['access_key'] == 'foo'

