"""
Tests for air_api.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,protected-access,arguments-differ

from json import JSONDecodeError
from unittest import TestCase
from unittest.mock import MagicMock, patch
import pytest
from cumulus_air_sdk import AirApi
import cumulus_air_sdk.air_sdk as sdk

class TestAirApi(TestCase):
    @patch('requests.Session')
    def setUp(self, mock_session):
        self.session = mock_session
        self.req = self.session.return_value
        self.session.return_value.headers = {}
        self.api = AirApi('http://test/api/', 'v1')

    def test_init(self):
        self.assertEqual(self.api.api, self.req)
        self.assertEqual(self.api.api.headers['content-type'], 'application/json')
        self.assertEqual(self.api.api_url, 'http://test/api/v1')
        self.assertEqual(self.api.token, '')

        # Assert API helpers are loaded
        self.assertIsInstance(self.api.node, sdk.NodeApi)
        self.assertIsInstance(self.api.permission, sdk.PermissionApi)
        self.assertIsInstance(self.api.service, sdk.ServiceApi)
        self.assertIsInstance(self.api.simulation, sdk.SimulationApi)
        self.assertIsInstance(self.api.simulation_interface, sdk.SimulationInterfaceApi)
        self.assertIsInstance(self.api.topology, sdk.TopologyApi)
        self.assertIsInstance(self.api.simulation_node, sdk.SimulationNodeApi)
        self.assertIsInstance(self.api.capacity, sdk.CapacityApi)
        self.assertIsInstance(self.api.worker, sdk.WorkerApi)

    def test_authorize_token(self):
        self.api.authorize(token='foo')
        self.assertEqual(self.api.token, 'foo')
        self.assertEqual(self.api.api.headers['authorization'], 'Bearer foo')

    def test_authorize_password(self):
        self.api.get_token = MagicMock(return_value='abc123')
        self.api.authorize(username='foo', password='bar')
        self.assertEqual(self.api.token, 'abc123')
        self.assertEqual(self.api.api.headers['authorization'], 'Bearer abc123')

    def test_authorize_bad_args(self):
        with pytest.raises(ValueError) as err:
            self.api.authorize()
            self.assertEqual(err.value, 'AirApi.authorize() requires either `token` or ' + \
                                        '`username` and `password` arguments')

    def test_get_token(self):
        self.req.post.return_value.json.return_value = {'token': 'abc123'}
        res = self.api.get_token('foo', 'bar')
        self.assertEqual(res, 'abc123')
        self.req.post.assert_called_with('http://test/api/v1/login/',
                                         json={'username': 'foo', 'password': 'bar'})

    def test_get_token_no_token(self):
        self.req.post.return_value.json.return_value = {'redirect': 'http://test'}
        with self.assertRaises(sdk.AirAuthorizationError) as err:
            self.api.get_token('foo', 'bar')
        self.assertEqual(err.exception.message, 'API did not provide a token for foo')

    def test_get_token_bad_json(self):
        self.req.post.return_value.json.side_effect = JSONDecodeError('', '{}', 1)
        with self.assertRaises(sdk.AirAuthorizationError) as err:
            self.api.get_token('foo', 'bar')
        self.assertEqual(err.exception.message, 'API did not return a valid JSON response')

    def test_request(self):
        res = self.api._request('GET', 'http://test/', 'test', foo='bar')
        self.session.return_value.request.assert_called_with('GET', 'http://test/', 'test',
                                                             foo='bar')
        self.assertEqual(res, self.session.return_value.request.return_value)

    def test_request_403(self):
        self.session.return_value.request.return_value.status_code = 403
        with self.assertRaises(sdk.exceptions.AirForbiddenError):
            self.api._request('GET', 'http://test/', 'test', foo='bar')

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
