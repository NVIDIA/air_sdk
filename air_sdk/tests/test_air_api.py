"""
Tests for air_api.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring

from unittest import TestCase
from unittest.mock import MagicMock
import pytest
from requests import Session
import requests_mock
from cumulus_air_sdk import AirApi
import cumulus_air_sdk.air_sdk as sdk

class TestAirApi(TestCase):
    def setUp(self):
        self.api = AirApi('http://test/api/', 'v1')

    def test_init(self):
        self.assertIsInstance(self.api.api, Session)
        self.assertEqual(self.api.api.headers['content-type'], 'application/json')
        self.assertEqual(self.api.api_url, 'http://test/api/v1')
        self.assertEqual(self.api.token, '')

        # Assert API helpers are loaded
        self.assertIsInstance(self.api.simulation, sdk.Simulation)

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

    @requests_mock.Mocker()
    def test_get_token(self, mock_requests):
        mock_requests.post('http://test/api/v1/login/', json={'token': 'abc123'})
        res = self.api.get_token('foo', 'bar')
        self.assertEqual(res, 'abc123')

    @requests_mock.Mocker()
    def test_get_token_no_token(self, mock_requests):
        mock_requests.post('http://test/api/v1/login/', json={'redirect': 'http://test'})
        with pytest.raises(sdk.AirAuthorizationError) as err:
            self.api.get_token('foo', 'bar')
            self.assertEqual(err.value, 'API did not provide a token for foo')

    @requests_mock.Mocker()
    def test_get_token_bad_json(self, mock_requests):
        mock_requests.post('http://test/api/v1/login/')
        with pytest.raises(sdk.AirAuthorizationError) as err:
            self.api.get_token('foo', 'bar')
            self.assertEqual(err.value, 'API did not return a valid JSON response')

    def test_get(self):
        self.api.api.get = MagicMock()
        self.api.get('http://test/api/v1/foo/', 'arg1', arg2='test')
        self.api.api.get.assert_called_with('http://test/api/v1/foo/', 'arg1', arg2='test')

    def test_post(self):
        self.api.api.post = MagicMock()
        self.api.post('http://test/api/v1/foo/', 'arg1', arg2='test')
        self.api.api.post.assert_called_with('http://test/api/v1/foo/', 'arg1', arg2='test')

    def test_put(self):
        self.api.api.put = MagicMock()
        self.api.put('http://test/api/v1/foo/', 'arg1', arg2='test')
        self.api.api.put.assert_called_with('http://test/api/v1/foo/', 'arg1', arg2='test')

    def test_patch(self):
        self.api.api.patch = MagicMock()
        self.api.patch('http://test/api/v1/foo/', 'arg1', arg2='test')
        self.api.api.patch.assert_called_with('http://test/api/v1/foo/', 'arg1', arg2='test')

    def test_delete(self):
        self.api.api.delete = MagicMock()
        self.api.delete('http://test/api/v1/foo/', 'arg1', arg2='test')
        self.api.api.delete.assert_called_with('http://test/api/v1/foo/', 'arg1', arg2='test')
