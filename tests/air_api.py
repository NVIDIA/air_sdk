# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for air_api.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,protected-access
#pylint: disable=arguments-differ,unused-argument,no-member,too-many-public-methods

from json import JSONDecodeError
from unittest import TestCase
from unittest.mock import MagicMock, patch
import datetime as dt

import pytest
import requests

from ..air_sdk import air_api
from ..air_sdk.account import AccountApi
from ..air_sdk.air_model import AirModel, LazyLoaded
from ..air_sdk.capacity import CapacityApi
from ..air_sdk.demo import DemoApi
from ..air_sdk.exceptions import AirAuthorizationError, AirForbiddenError, AirUnexpectedResponse
from ..air_sdk.image import ImageApi
from ..air_sdk.interface import InterfaceApi
from ..air_sdk.job import JobApi
from ..air_sdk.link import LinkApi
from ..air_sdk.login import LoginApi
from ..air_sdk.marketplace import MarketplaceApi
from ..air_sdk.node import NodeApi
from ..air_sdk.organization import OrganizationApi
from ..air_sdk.permission import PermissionApi
from ..air_sdk.service import ServiceApi
from ..air_sdk.ssh_key import SSHKeyApi
from ..air_sdk.simulation import SimulationApi
from ..air_sdk.simulation_interface import SimulationInterfaceApi
from ..air_sdk.simulation_node import SimulationNodeApi
from ..air_sdk.token import TokenApi
from ..air_sdk.topology import TopologyApi
from ..air_sdk.worker import WorkerApi

class TestAirSession(TestCase):
    def setUp(self):
        self.session = air_api.AirSession()

    def test_init(self):
        self.assertIsInstance(self.session, requests.Session)

    @patch('air_sdk.air_sdk.air_api.requests.Session.rebuild_auth')
    @patch('air_sdk.air_sdk.air_api.urlparse')
    def test_rebuild_auth_allowed(self, mock_parse, mock_rebuild):
        mock_url = MagicMock()
        mock_url.hostname = 'air.nvidia.com'
        mock_parse.return_value = mock_url
        mock_req = MagicMock()
        self.session.rebuild_auth(mock_req, None)
        mock_parse.assert_called_with(mock_req.url)
        mock_rebuild.assert_not_called()

    @patch('air_sdk.air_sdk.air_api.requests.Session.rebuild_auth')
    @patch('air_sdk.air_sdk.air_api.urlparse')
    def test_rebuild_auth_not_allowed(self, mock_parse, mock_rebuild):
        mock_url = MagicMock()
        mock_url.hostname = 'air.evil.com'
        mock_parse.return_value = mock_url
        mock_req = MagicMock()
        mock_res = MagicMock()
        self.session.rebuild_auth(mock_req, mock_res)
        mock_rebuild.assert_called_with(mock_req, mock_res)

class TestAirApi(TestCase):
    @patch('air_sdk.air_sdk.air_api.AirSession')
    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def setUp(self, mock_raise, mock_session):
        self.session = mock_session
        self.req = self.session.return_value
        self.req.headers = {}
        self.api = air_api.AirApi('http://test/api/', 'v1', bearer_token='foo')

    def test_init(self):
        self.assertEqual(self.api.client, self.req)
        self.assertEqual(self.api.client.headers['content-type'], 'application/json')
        self.assertEqual(self.api.api_url, 'http://test/api/v1')
        self.assertEqual(self.api.token, 'foo')
        self.assertIsNone(self.api.username)

    @patch('air_sdk.air_sdk.air_api.AirApi.authorize')
    def test_init_authorize(self, mock_auth):
        self.api = air_api.AirApi('http://test/api/', 'v1', bearer_token='foo')
        mock_auth.assert_called_with(bearer_token='foo')

    def test_accounts(self):
        self.assertIsInstance(self.api.accounts, AccountApi)

    def test_api_tokens(self):
        self.assertIsInstance(self.api.api_tokens, TokenApi)

    def test_capacity(self):
        self.assertIsInstance(self.api.capacity, CapacityApi)

    def test_demos(self):
        self.assertIsInstance(self.api.demos, DemoApi)

    def test_images(self):
        self.assertIsInstance(self.api.images, ImageApi)

    def test_interfaces(self):
        self.assertIsInstance(self.api.interfaces, InterfaceApi)

    def test_jobs(self):
        self.assertIsInstance(self.api.jobs, JobApi)

    def test_links(self):
        self.assertIsInstance(self.api.links, LinkApi)

    def test_login(self):
        self.assertIsInstance(self.api.login, LoginApi)

    def test_marketplace(self):
        self.assertIsInstance(self.api.marketplace, MarketplaceApi)

    def test_node(self):
        self.assertIsInstance(self.api.node, NodeApi)

    def test_nodes(self):
        self.assertIsInstance(self.api.nodes, NodeApi)

    def test_organizations(self):
        self.assertIsInstance(self.api.organizations, OrganizationApi)

    def test_permission(self):
        self.assertIsInstance(self.api.permission, PermissionApi)

    def test_permissions(self):
        self.assertIsInstance(self.api.permissions, PermissionApi)

    def test_service(self):
        self.assertIsInstance(self.api.service, ServiceApi)

    def test_services(self):
        self.assertIsInstance(self.api.services, ServiceApi)

    def test_simulation(self):
        self.assertIsInstance(self.api.simulation, SimulationApi)

    def test_simulations(self):
        self.assertIsInstance(self.api.simulations, SimulationApi)

    def test_simulation_interface(self):
        self.assertIsInstance(self.api.simulation_interface, SimulationInterfaceApi)

    def test_simulation_interfaces(self):
        self.assertIsInstance(self.api.simulation_interfaces, SimulationInterfaceApi)

    def test_simulation_node(self):
        self.assertIsInstance(self.api.simulation_node, SimulationNodeApi)

    def test_simulation_nodes(self):
        self.assertIsInstance(self.api.simulation_nodes, SimulationNodeApi)

    def test_ssh_keys(self):
        self.assertIsInstance(self.api.ssh_keys, SSHKeyApi)

    def test_topology(self):
        self.assertIsInstance(self.api.topology, TopologyApi)

    def test_topologies(self):
        self.assertIsInstance(self.api.topologies, TopologyApi)

    def test_worker(self):
        self.assertIsInstance(self.api.worker, WorkerApi)

    def test_workers(self):
        self.assertIsInstance(self.api.workers, WorkerApi)

    @patch('air_sdk.air_sdk.login.LoginApi.list')
    def test_authorize_token(self, mock_login):
        mock_login.return_value.username = 'john'
        self.api.authorize(bearer_token='foo')
        self.assertEqual(self.api.token, 'foo')
        self.assertEqual(self.api.client.headers['authorization'], 'Bearer foo')
        self.assertEqual(self.api.username, 'john')

    @patch('air_sdk.air_sdk.login.LoginApi.list')
    def test_authorize_password(self, mock_login):
        mock_login.return_value.username = 'john'
        self.api.get_token = MagicMock(return_value='abc123')
        self.api.authorize(username='foo', password='bar')
        self.assertEqual(self.api.token, 'abc123')
        self.assertEqual(self.api.client.headers['authorization'], 'Bearer abc123')
        self.assertEqual(self.api.username, 'john')

    def test_authorize_bad_args(self):
        with pytest.raises(ValueError) as err:
            self.api.authorize()
        self.assertEqual(str(err.value), 'Must include either `bearer_token` or ' + \
                                         '`username` and `password` arguments')

    @patch('air_sdk.air_sdk.air_api.AirApi.post')
    def test_get_token(self, mock_post):
        mock_post.return_value.json.return_value = {'token': 'abc123'}
        res = self.api.get_token('foo', 'bar')
        self.assertEqual(res, 'abc123')
        mock_post.assert_called_with('http://test/api/v1/login/',
                                     json={'username': 'foo', 'password': 'bar'})

    @patch('air_sdk.air_sdk.air_api.AirApi.post')
    def test_get_token_no_token(self, mock_post):
        mock_post.return_value.json.return_value = {'redirect': 'http://test'}
        with self.assertRaises(AirAuthorizationError) as err:
            self.api.get_token('foo', 'bar')
        self.assertEqual(err.exception.message, 'API did not provide a token for foo')

    @patch('air_sdk.air_sdk.air_api.AirApi.post')
    def test_get_token_bad_json(self, mock_post):
        mock_post.return_value.json.side_effect = JSONDecodeError('', '{}', 1)
        with self.assertRaises(AirAuthorizationError) as err:
            self.api.get_token('foo', 'bar')
        self.assertEqual(err.exception.message, 'API did not return a valid JSON response')

    def test_request(self):
        res = self.api._request('GET', 'http://test/', 'test', foo='bar')
        self.api.client.request.assert_called_with('GET', 'http://test/', 'test',
                                                   allow_redirects=False, foo='bar')
        self.assertEqual(res, self.api.client.request.return_value)

    def test_request_403(self):
        self.api.client.request.return_value.status_code = 403
        with self.assertRaises(AirForbiddenError):
            self.api._request('GET', 'http://test/', 'test', foo='bar')

    def test_request_raises(self):
        mock_res = MagicMock()
        self.api.client.request.return_value.raise_for_status = \
            MagicMock(side_effect=requests.exceptions.HTTPError(response=mock_res))
        with self.assertRaises(AirUnexpectedResponse) as err:
            self.api._request('GET', 'http://test/', 'test', foo='bar')
        self.assertEqual(err.exception.message,
                         'Received an unexpected response from the Air API ' + \
                         f'({mock_res.status_code}): {mock_res.text}')
        self.assertEqual(err.exception.status_code, mock_res.status_code)

    @patch('air_sdk.air_sdk.air_api._serialize_dict')
    def test_request_serialized_json_list(self, mock_serialize):
        serialized = ['serialized_foo', 'serialized_bar']
        mock_serialize.side_effect = serialized
        data = ['foo', 'bar']
        self.api._request('GET', 'http://test/', json=data)
        mock_for_assert = MagicMock()
        mock_for_assert(data[0])
        mock_for_assert(data[1])
        self.assertEqual(mock_serialize.mock_calls, mock_for_assert.mock_calls)
        self.api.client.request.assert_called_with('GET', 'http://test/', allow_redirects=False,
                                                   json=[serialized[0], serialized[1]])

    @patch('air_sdk.air_sdk.air_api._serialize_dict')
    def test_request_serialized_json(self, mock_serialize):
        self.api._request('GET', 'http://test/', json='foo')
        mock_serialize.assert_called_with('foo')
        self.api.client.request.assert_called_with('GET', 'http://test/', allow_redirects=False,
                                                   json=mock_serialize.return_value)

    @patch('air_sdk.air_sdk.air_api._serialize_dict')
    def test_request_serialized_params(self, mock_serialize):
        self.api._request('GET', 'http://test/', params='foo')
        mock_serialize.assert_called_with('foo')
        self.api.client.request.assert_called_with('GET', 'http://test/', allow_redirects=False,
                                                   params=mock_serialize.return_value)

    def test_request_redirect(self):
        self.api.client.request.return_value.status_code = 301
        self.api.client.request.return_value.headers = {'Location': 'http://air.nvidia.com/'}
        self.api._request('GET', 'http://test/', json={'foo': 'bar'})
        self.api.client.request.assert_called_with('GET', 'http://air.nvidia.com/',
                                                   json={'foo': 'bar'})
        self.assertEqual(self.api.client.request.call_count, 3)

    def test_request_redirect_ignored(self):
        self.api.client.request.return_value.status_code = 301
        self.api.client.request.return_value.headers = {'Location': 'http://air.evil.com/'}
        self.api._request('GET', 'http://test/', json={'foo': 'bar'})
        self.assertEqual(self.api.client.request.call_count, 2)

    def test_get(self):
        self.api._request = MagicMock()
        self.api.get('http://test/api/v1/foo/', 'arg1', arg2='test')
        self.api._request.assert_called_with('GET', 'http://test/api/v1/foo/', 'arg1', arg2='test')

    def test_post(self):
        self.api._request = MagicMock()
        self.api.post('http://test/api/v1/foo/', 'arg1', arg2='test')
        self.api._request.assert_called_with('POST', 'http://test/api/v1/foo/', 'arg1', arg2='test')

    def test_put(self):
        self.api._request = MagicMock()
        self.api.put('http://test/api/v1/foo/', 'arg1', arg2='test')
        self.api._request.assert_called_with('PUT', 'http://test/api/v1/foo/', 'arg1', arg2='test')

    def test_patch(self):
        self.api._request = MagicMock()
        self.api.patch('http://test/api/v1/foo/', 'arg1', arg2='test')
        self.api._request.assert_called_with('PATCH', 'http://test/api/v1/foo/', 'arg1',
                                             arg2='test')

    def test_delete(self):
        self.api._request = MagicMock()
        self.api.delete('http://test/api/v1/foo/', 'arg1', arg2='test')
        self.api._request.assert_called_with('DELETE', 'http://test/api/v1/foo/', 'arg1',
                                             arg2='test')

class TestHelpers(TestCase):
    def test_normalize_api_version(self):
        res = air_api._normalize_api_version('v1')
        self.assertEqual(res, 'v1')

    def test_normalize_api_version_str(self):
        res = air_api._normalize_api_version('1')
        self.assertEqual(res, 'v1')

    def test_normalize_api_version_int(self):
        res = air_api._normalize_api_version(1)
        self.assertEqual(res, 'v1')

    def test_normalize_api_url(self):
        res = air_api._normalize_api_url('http://localhost/api/')
        self.assertEqual(res, 'http://localhost/api/')

    def test_normalize_api_url_nothing(self):
        res = air_api._normalize_api_url('http://localhost')
        self.assertEqual(res, 'http://localhost/api/')

    def test_normalize_api_url_no_slash(self):
        res = air_api._normalize_api_url('http://localhost/api')
        self.assertEqual(res, 'http://localhost/api/')

    def test_serialize_dict_air_model(self):
        mock_model = AirModel(MagicMock(), id='abc123')
        test_dict = {'test': mock_model}
        res = air_api._serialize_dict(test_dict)
        self.assertDictEqual(res, {'test': 'abc123'})

    def test_serialize_dict_lazy_load(self):
        mock_model = LazyLoaded('abc123', 'test')
        test_dict = {'test': mock_model}
        res = air_api._serialize_dict(test_dict)
        self.assertDictEqual(res, {'test': 'abc123'})

    def test_serialize_dict_dict(self):
        test_dict = {'test': {'foo': 'bar'}}
        res = air_api._serialize_dict(test_dict)
        self.assertDictEqual(res, {'test': {'foo': 'bar'}})

    @patch('air_sdk.air_sdk.air_api._serialize_list')
    def test_serialize_dict_list(self, mock_list):
        test_dict = {'test': ['foo']}
        res = air_api._serialize_dict(test_dict)
        mock_list.assert_called_with(['foo'])
        self.assertDictEqual(res, {'test': mock_list.return_value})

    def test_serialize_dict_datetime(self):
        time = dt.datetime(2030, 12, 12, 22, 5, 3)
        test_dict = {'test': {'foo': time}}
        res = air_api._serialize_dict(test_dict)
        self.assertDictEqual(res, {'test': {'foo': '2030-12-12T22:05:03'}})

    def test_serialize_dict(self):
        test_dict = {'test': 'foo'}
        res = air_api._serialize_dict(test_dict)
        self.assertDictEqual(res, {'test': 'foo'})

    def test_serialize_dict_private(self):
        test_dict = {'test': 'foo', '_private': 'bar'}
        res = air_api._serialize_dict(test_dict)
        self.assertDictEqual(res, {'test': 'foo'})

    def test_serialize_list_air_model(self):
        mock_model = AirModel(MagicMock(), id='abc123')
        test_list = [mock_model]
        res = air_api._serialize_list(test_list)
        self.assertListEqual(res, ['abc123'])

    def test_serialize_list_lazy_load(self):
        mock_model = LazyLoaded('abc123', 'test')
        test_list = [mock_model]
        res = air_api._serialize_list(test_list)
        self.assertListEqual(res, ['abc123'])

    @patch('air_sdk.air_sdk.air_api._serialize_dict')
    def test_serialize_list_dict(self, mock_dict):
        test_list = [{'foo': 'bar'}]
        mock_dict.called_with({'foo': 'bar'})
        res = air_api._serialize_list(test_list)
        self.assertListEqual(res, [mock_dict.return_value])

    def test_serialize_list_list(self):
        test_list = [['foo']]
        res = air_api._serialize_list(test_list)
        self.assertListEqual(res, test_list)

    def test_serialize_list(self):
        test_list = ['test']
        res = air_api._serialize_list(test_list)
        self.assertListEqual(res, ['test'])

    def test_serialize_list_private(self):
        test_list = ['_private', 'test']
        res = air_api._serialize_list(test_list)
        self.assertListEqual(res, ['test'])
