"""
Cumulus AIR API module
"""

import logging
from json import JSONDecodeError
import requests
from .exceptions import AirAuthorizationError
from .node import NodeApi
from .permission import PermissionApi
from .service import ServiceApi
from .simulation import SimulationApi
from .simulation_interface import SimulationInterfaceApi
from .topology import TopologyApi

class AirApi:
    """
    API Client instance
    """
    def __init__(self, api_url='https://air.cumulusnetworks.com/api/', api_version='v1'):
        self.api = requests.Session()
        self.api.headers.update({'content-type': 'application/json'})
        self.api_url = api_url + api_version
        self.token = ''
        self.node = NodeApi(self)
        self.permission = PermissionApi(self)
        self.service = ServiceApi(self)
        self.simulation = SimulationApi(self)
        self.simulation_interface = SimulationInterfaceApi(self)
        self.topology = TopologyApi(self)

    def authorize(self, **kwargs):
        """
        Authorizes the API client using either a bearer token or a username/password.
        Callers MUST pass either a valid `token` or a `username` and `password`.
        After successfully authorizing, all subsequent API calls will include the
        authorization token provided by the AIR API.

        Arguments:
        token [str] - Bearer token
        username [str] - Username
        password [str] - Password

        Raises:
        ValueError - Raised when the caller does not pass either a token or a username/password
        """
        if kwargs.get('token', None):
            token = kwargs['token']
        elif kwargs.get('username', None) and kwargs.get('password', None):
            token = self.get_token(kwargs['username'], kwargs['password'])
        else:
            raise ValueError('AirApi.authorize() requires either `token` or ' + \
                           '`username` and `password` arguments')
        self.token = token
        self.api.headers.update({'authorization': 'Bearer ' + token})

    def get_token(self, username, password):
        """
        Gets a new bearer token for a given username and password

        Arguments:
        username (str) - Username
        password (str) - Password

        Returns:
        (str) Bearer token

        Raises:
        AirAuthorizationError - Raised when the API does not return a token for any reason
        JSONDecodeError - Raised when the API's response is not a valid JSON object
        """
        route = '/login/'
        data = {'username': username, 'password': password}
        res = self.api.post(self.api_url + route, json=data)
        try:
            if res.json().get('token', None):
                return res.json()['token']
            logging.debug('AirApi.get_token :: Response JSON')
            logging.debug(res.json())
            raise AirAuthorizationError('API did not provide a token for ' + username)
        except JSONDecodeError:
            raise AirAuthorizationError('API did not return a valid JSON response')

    def get(self, url, *args, **kwargs):
        """ Wrapper method for GET requests """
        return self.api.get(url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        """ Wrapper method for POST requests """
        return self.api.post(url, *args, **kwargs)

    def put(self, url, *args, **kwargs):
        """ Wrapper method for PUT requests """
        return self.api.put(url, *args, **kwargs)

    def patch(self, url, *args, **kwargs):
        """ Wrapper method for PATCH requests """
        return self.api.patch(url, *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        """ Wrapper method for DELETE requests """
        return self.api.delete(url, *args, **kwargs)
