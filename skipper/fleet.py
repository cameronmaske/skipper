import requests
from requests.exceptions import HTTPError
import json


class FleetException(Exception):
    pass


class NotFound(FleetException):
    pass


class Fleet(object):
    """
    Docs: https://github.com/coreos/fleet/blob/master/Documentation/api-v1-alpha.md
    """

    NotFound = NotFound

    def __init__(self, port):
        self.port = port

    @property
    def base_uri(self):
        """URI used by the client to connect to fleet."""
        return "http://localhost:%s/v1-alpha/" % self.port

    def _parse_response(self, response):
        """
        Parse an API response. Raises any errors.
        """
        try:
            response.raise_for_status()
        except HTTPError:
            if response.status_code == 404:
                raise self.NotFound
            else:
                raise FleetException(response.content)

        if response.content:
            return response.json()

    def _construct_request_data(self, method, params):
        """
        Based on the request methods, attaches params to either the url
        for GET's or the body.
        """
        request_parmas = {}
        if method in ('POST', 'PUT', 'DELETE'):
            request_parmas['data'] = json.dumps(params)
        elif method == 'GET':
            request_parmas['params'] = params

        return request_parmas

    def _construct_request(self, method, endpoint, params=None, timeout=30):
        """
        Construct the request params.
        """
        request_parmas = {}
        request_parmas['method'] = method
        request_parmas['url'] = "".join([self.base_uri, endpoint])
        request_parmas['headers'] = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        request_parmas['timeout'] = timeout
        request_parmas.update(
            self._construct_request_data(method, params)
        )
        return request_parmas

    def _call(self, method, endpoint, params=None, timeout=30):
        """
        Sends out an API request and parses the response.
        """
        request_parmas = self._construct_request(method, endpoint, params, timeout)
        response = requests.request(**request_parmas)
        return self._parse_response(response)

    def list_machines(self):
        """
        Returns a list of machines registered to the fleet cluster.
        """
        response = self._call("GET", "machines")
        return response.get("machines", [])

    def list_states(self, machine_id=None, unit_name=None):
        """
        List the state of all units.
        """
        params = {}
        if machine_id:
            params["machineId"] = machine_id
        if unit_name:
            params["unitName"] = unit_name
        response = self._call("GET", "state", params=params)
        return response.get("states", [])

    def list_units(self):
        """
        List all units.
        """
        response = self._call("GET", "units")
        return response.get("units", [])

    def get_unit(self, name):
        """
        Get a unit.
        """
        response = self._call("GET", "units/%s.service" % name)
        return response

    def delete_unit(self, name):
        """
        Delete a unit.
        """
        self._call("DELETE", "units/%s.service" % name)

    def create_unit(self, machine_id, name, options, state="launched"):
        """
        Create a unit.
        """
        return self._call(
            "PUT",
            "units/%s.service" % name,
            params={
                "desiredState": state,
                "machineId": machine_id,
                "name": "%s.service" % name,
                "options": options
            }
        )
