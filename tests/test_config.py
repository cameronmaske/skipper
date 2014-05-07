from skipper.config import BaseConfig


def test_config():
    config = BaseConfig()
    assert config == {}
    config['foo'] = 'bar'
    assert config != {}


def test_config_get():
    config = BaseConfig()
    config['foo'] = 'bar'
    assert config['foo'] == 'bar'
    assert config.get('foo') == 'bar'


def test_config_del():
    config = BaseConfig()
    config['foo'] = 'bar'
    del config['foo']
    assert config == {}

