import pytest
import mock

from skipper.creds import Creds


@pytest.fixture()
def creds():
    storage = mock.MagicMock()
    storage.retrieve.return_value = {}
    creds = Creds(storage=storage)
    return creds


def test_creds(creds):
    assert creds == {}
    creds['foo'] = 'bar'
    assert creds == {'foo': 'bar'}
    creds.storage.save.assert_called_with({'foo': 'bar'})


def test_creds_get(creds):
    creds['foo'] = 'bar'
    assert creds['foo'] == 'bar'
    assert creds.get('foo') == 'bar'


def test_creds_del(creds):
    creds['foo'] = 'bar'
    del creds['foo']
    assert creds == {}
    creds.storage.save.assert_called_with({})


def test_nested_creds(creds):
    assert creds['foo']['bar'] == {}
    creds['foo']['bar'] = 'buzz'
    assert creds['foo']['bar'] == 'buzz'
    creds.storage.save.assert_called_once_with({
        'foo': {
            'bar': 'buzz'
        }})


def test_config_retrieve():
    storage = mock.MagicMock()
    existing = {
        'foo': 'bar',
        'foo2': {
            'bar2': 'buzz'
        }
    }
    storage.retrieve.return_value = existing
    creds = Creds(storage=storage)
    assert creds == existing
    assert storage.retrieve.called
