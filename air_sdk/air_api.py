# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
NVIDIA Air API module
"""

from datetime import date, datetime
from json import JSONDecodeError

import requests
from requests.compat import urlparse

from . import util, const
from .account import AccountApi
from .air_model import AirModel, LazyLoaded
from .capacity import CapacityApi
from .demo import DemoApi
from .exceptions import AirAuthorizationError, AirForbiddenError, AirUnexpectedResponse
from .fleet import FleetApi
from .image import ImageApi
from .interface import InterfaceApi
from .job import JobApi
from .link import LinkApi
from .logger import air_sdk_logger as logger
from .login import LoginApi
from .marketplace import MarketplaceApi
from .node import NodeApi
from .organization import OrganizationApi
from .permission import PermissionApi
from .resource_budget import ResourceBudgetApi
from .service import ServiceApi
from .simulation import SimulationApi
from .simulation_interface import SimulationInterfaceApi
from .simulation_node import SimulationNodeApi
from .ssh_key import SSHKeyApi
from .token import TokenApi
from .topology import TopologyApi
from .topology_file import TopologyFileApi
from .userconfig import UserConfigAPI
from .worker import WorkerApi


class AirSession(requests.Session):
    """Wrapper around requests.Session"""

    default_connect_timeout = const.DEFAULT_CONNECT_TIMEOUT
    default_read_timeout = const.DEFAULT_READ_TIMEOUT

    def rebuild_auth(self, prepared_request, response):
        """Allow credential sharing between nvidia.com and cumulusnetworks.com only"""
        if urlparse(prepared_request.url).hostname in const.ALLOWED_HOSTS:
            return
        super().rebuild_auth(prepared_request, response)

    def request(self, method, url, **kwargs):
        """Override request method to pass the timeout"""
        connect_timeout = kwargs.pop('default_connect_timeout', self.default_connect_timeout)
        read_timeout = kwargs.pop('default_read_timeout', self.default_read_timeout)
        kwargs.setdefault('timeout', (connect_timeout, read_timeout))
        return super().request(method, url, **kwargs)


class AirApi:
    """
    Main interface for an API client instance
    """

    def __init__(self, api_url=const.DEFAULT_API_URL, api_version='v1', **kwargs):
        """
        Create a new API client instance. The caller MUST provide either `username` and `password`
        or a `bearer_token`. The `password` argument may either be an API token or a service account
        password.

        Arguments:
            username (str, optional): Username
            password (str, optional): Password or API token
            bearer_token (str, optional): Pre-generated bearer token
            api_url (str, optional): Default = https://air.nvidia.com/api/
            api_version (str): Default = v1
        """
        self.client = AirSession()
        self.client.headers.update({'content-type': 'application/json'})

        self.api_url = _normalize_api_url(api_url) + _normalize_api_version(api_version)
        self._kwargs = kwargs
        self.token = None
        self.username = None
        self.authorize(**kwargs)

    @property
    def accounts(self):
        return AccountApi(self)

    @property
    def api_tokens(self):
        return TokenApi(self)

    @property
    def capacity(self):
        return CapacityApi(self)

    @property
    def demos(self):
        return DemoApi(self)

    @property
    def fleets(self):
        return FleetApi(self)

    @property
    def images(self):
        return ImageApi(self)

    @property
    def interfaces(self):
        return InterfaceApi(self)

    @property
    def jobs(self):
        return JobApi(self)

    @property
    def links(self):
        return LinkApi(self)

    @property
    def login(self):
        return LoginApi(self)

    @property
    def marketplace(self):
        return MarketplaceApi(self)

    @property
    @util.deprecated('AirApi.nodes')
    def node(self):
        return self.nodes

    @property
    def nodes(self):
        return NodeApi(self)

    @property
    def organizations(self):
        return OrganizationApi(self)

    @property
    @util.deprecated('AirApi.permissions')
    def permission(self):
        return self.permissions

    @property
    def permissions(self):
        return PermissionApi(self)

    @property
    def resource_budgets(self):
        return ResourceBudgetApi(self)

    @property
    @util.deprecated('AirApi.services')
    def service(self):
        return self.services

    @property
    def services(self):
        return ServiceApi(self)

    @property
    @util.deprecated('AirApi.simulations')
    def simulation(self):
        return self.simulations

    @property
    def simulations(self):
        return SimulationApi(self)

    @property
    @util.deprecated('AirApi.simulation_interfaces')
    def simulation_interface(self):
        return self.simulation_interfaces

    @property
    def simulation_interfaces(self):
        return SimulationInterfaceApi(self)

    @property
    @util.deprecated('AirApi.simulation_nodes')
    def simulation_node(self):
        return self.simulation_nodes

    @property
    def simulation_nodes(self):
        return SimulationNodeApi(self)

    @property
    def ssh_keys(self):
        return SSHKeyApi(self)

    @property
    @util.deprecated('AirApi.topologies')
    def topology(self):
        return self.topologies

    @property
    def topology_files(self):
        return TopologyFileApi(self)

    @property
    def topologies(self):
        return TopologyApi(self)

    @property
    @util.deprecated('AirApi.workers')
    def worker(self):
        return self.workers

    @property
    def workers(self):
        return WorkerApi(self)

    @property
    def user_configs(self):
        return UserConfigAPI(self)

    def authorize(self, **kwargs):
        """
        Authorizes the API client using either a pre-generated API token, a service account
        username/password, or a pre-generated bearer token.
        Callers MUST pass either a valid `bearer_token` or a `username` and `password`.
        The `password` argument may either be an API token or a service account
        password. After successfully authorizing, all subsequent API calls will include the
        authorization token provided by the AIR API. **Note:** This is called once automatically
        when an AirApi object is instantiated.

        Arguments:
            bearer_token (str, optional): Pre-generated bearer token
            username (str, optional): Username
            password (str, optional): Password or API token

        Raises:
            ValueError - Caller did not pass either a token or a username/password
        """
        token = None
        if kwargs.get('bearer_token'):
            token = kwargs['bearer_token']
        elif kwargs.get('username', None) and kwargs.get('password', None):
            token = self.get_token(kwargs['username'], kwargs['password'])
        else:
            raise ValueError('Must include either `bearer_token` or ' + '`username` and `password` arguments')
        self.token = token
        self.client.headers.update({'authorization': 'Bearer ' + token})
        login = self.login.list()
        self.username = getattr(login, 'username', None)

    def get_token(self, username, password):
        """
        Gets a new bearer token for a given username and password

        Arguments:
            username (str): Username
            password (str): Password

        Returns:
            str: Bearer token

        Raises:
            - [`AirAuthorizationError`](/docs/exceptions) - API did not return a token
            - `JSONDecodeError` - API's response is not a valid JSON object
        """
        route = '/login/'
        data = {'username': username, 'password': password}
        res = self.post(self.api_url + route, json=data, attempt_reauth=False)
        try:
            if res.json().get('token', None):
                return res.json()['token']
            logger.debug('AirApi.get_token :: Response JSON')
            logger.debug(res.json())
            raise AirAuthorizationError('API did not provide a token for ' + username)
        except JSONDecodeError:
            raise AirAuthorizationError('API did not return a valid JSON response')

    def _request(self, method, url, *args, **kwargs):
        attempt_reauth = kwargs.pop('attempt_reauth', True)
        if kwargs.get('json'):
            logger.debug(f'unserialized json: {kwargs["json"]}')
            if isinstance(kwargs['json'], list):
                kwargs['json'] = [_serialize_dict(obj) for obj in kwargs['json']]
            else:
                kwargs['json'] = _serialize_dict(kwargs['json'])
        if kwargs.get('params'):
            kwargs['params'] = _serialize_dict(kwargs['params'])
        logger.debug(f'request args: {args}')
        logger.debug(f'request kwargs: {kwargs}')
        res = self.client.request(method, url, allow_redirects=False, *args, **kwargs)
        if res.status_code == 301 and urlparse(res.headers.get('Location')).hostname in const.ALLOWED_HOSTS:
            res = self.client.request(method, res.headers['Location'], *args, **kwargs)
        if getattr(res, 'status_code') == 403:
            missing_creds_err_msg = '{"detail":"Authentication credentials were not provided."}'
            if attempt_reauth and self._kwargs.get('username') and self._kwargs.get('password'):
                logger.debug('Request failed with 403, attempting reauth')
                self.authorize(**self._kwargs)
                return self._request(method, url, *args, **{'attempt_reauth': False, **kwargs})
            if res.text != missing_creds_err_msg:
                raise AirForbiddenError(res.text)
            else:
                raise AirForbiddenError
        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise AirUnexpectedResponse(err.response.text, err.response.status_code)
        return res

    def get(self, url, *args, **kwargs):
        """Wrapper method for GET requests"""
        return self._request('GET', url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        """Wrapper method for POST requests"""
        return self._request('POST', url, *args, **kwargs)

    def put(self, url, *args, **kwargs):
        """Wrapper method for PUT requests"""
        return self._request('PUT', url, *args, **kwargs)

    def patch(self, url, *args, **kwargs):
        """Wrapper method for PATCH requests"""
        return self._request('PATCH', url, *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        """Wrapper method for DELETE requests"""
        return self._request('DELETE', url, *args, **kwargs)


def _normalize_api_version(version):
    try:
        version = int(version)
        version = f'v{version}'
    except Exception:
        pass
    return version


def _normalize_api_url(url: str) -> str:
    if url[-1] != '/':
        url += '/'
    if not url.endswith('api/'):
        url += 'api/'
    return url


def _serialize_dict(raw_dict):
    clone = {}
    for key, value in raw_dict.items():
        if isinstance(value, (AirModel, LazyLoaded)):
            clone[key] = value.id
        elif isinstance(value, dict):
            clone[key] = _serialize_dict(value)
        elif isinstance(value, list):
            clone[key] = _serialize_list(value)
        elif isinstance(value, (datetime, date)):
            clone[key] = value.isoformat()
        elif not key.startswith('_'):
            clone[key] = value
    return clone


def _serialize_list(raw_list):
    clone = []
    for item in raw_list:
        if isinstance(item, (AirModel, LazyLoaded)):
            clone.append(item.id)
        elif isinstance(item, dict):
            clone.append(_serialize_dict(item))
        elif isinstance(item, list):
            clone.append(_serialize_list(item))
        elif not str(item).startswith('_'):
            clone.append(item)
    return clone
