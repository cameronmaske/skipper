import pytest
import httpretty
import mock


def test_init(fleet):
    assert fleet.port == 6001
    assert fleet.base_uri == "http://localhost:6001/v1-alpha/"


def test_parse_response(fleet, response):
    response.json.return_value = {"foo": "bar"}
    assert fleet._parse_response(response) == {"foo": "bar"}
    assert response.raise_for_status.called


def test_request_construct_request_data_get(fleet):
    request_params = fleet._construct_request_data(
        'GET', {"foo": "bar"})
    assert request_params == {
        "params": {"foo": "bar"}
    }


def test_request_construct_request_data_post(fleet):
    request_params = fleet._construct_request_data('POST', {"foo": "bar"})
    assert request_params == {
        "data": '{"foo": "bar"}'
    }


def test_request_construct_request_data_put(fleet):
    request_params = fleet._construct_request_data('PUT', {"foo": "bar"})
    assert request_params == {
        "data": '{"foo": "bar"}'
    }


def test_request_construct_request_data_delete(fleet):
    request_params = fleet._construct_request_data('DELETE', {"foo": "bar"})
    assert request_params == {
        "data": '{"foo": "bar"}'
    }


def test_construct_request(fleet):
    request = fleet._construct_request("GET", "endpoint", {"foo": "bar"})
    assert request == {
        'url': "http://localhost:6001/v1-alpha/endpoint",
        'headers': {
            'Accept': "application/json",
            'Content-Type': "application/json"
        },
        'method': 'GET',
        'params': {"foo": "bar"},
        'timeout': 30
    }


@pytest.mark.integration
def test_call(fleet):
    httpretty.enable()
    httpretty.register_uri(
        httpretty.GET, "http://localhost:6001/v1-alpha/endpoint",
        body='{"foo": "bar"}',
        status=200
    )
    result = fleet._call('GET', 'endpoint', params={"foo": "bar"})
    assert result == {"foo": "bar"}


def test_list_machines(fleet):
    fleet._call = mock.Mock(return_value={"machines": [1]})
    machines = fleet.list_machines()
    fleet._call.assert_called_with("GET", "machines")
    assert machines == [1]


def test_list_states(fleet):
    fleet._call = mock.Mock(return_value={"states": [1]})
    states = fleet.list_states(machine_id=1, unit_name="unit")
    fleet._call.assert_called_with("GET", "state", params={
        "machineId": 1,
        "unitName": "unit"
    })
    assert states == [1]


def test_list_units(fleet):
    fleet._call = mock.Mock(return_value={"units": [1]})
    units = fleet.list_units()
    fleet._call.assert_called_with("GET", "units")
    assert units == [1]


def test_get_unit(fleet):
    fleet._call = mock.Mock(return_value={"foo": "bar"})
    units = fleet.get_unit("unit")
    fleet._call.assert_called_with("GET", "units/unit.service")
    assert units == {"foo": "bar"}


def test_delete_unit(fleet):
    fleet._call = mock.Mock()
    fleet.delete_unit("unit")
    fleet._call.assert_called_with("DELETE", "units/unit.service")


def test_create_unit(fleet):
    fleet._call = mock.Mock(return_value={"foo": "bar"})
    options = [
        {
            "section": "Unit",
            "name": "foo",
            "value": "bar"
        }
    ]
    units = fleet.create_unit(machine_id=1, name="unit", options=options)
    fleet._call.assert_called_with(
        "PUT", "units/unit.service", params={
            "desiredState": "launched",
            "machineId": 1,
            "name": "unit.service",
            "options": options
        })
    assert units == {"foo": "bar"}
