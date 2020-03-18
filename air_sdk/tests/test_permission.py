"""
Tests for permission.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring

from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock
import pytest
import requests_mock
from cumulus_air_sdk import AirApi
import cumulus_air_sdk.air_sdk as sdk

class TestPermission(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.data = {'url': 'http://test/api/v1/permission/abc', 'id': 'abc',
                     'email': 'test@test.com', 'account': 'def', 'topology': 'xyz',
                     'simulation': 'ghi', 'write_ok': True}
        self.permission = sdk.permission.Permission(self.api, **self.data)

    def test_init(self):
        self.assertEqual(self.permission.permission_api, self.api)
        data = deepcopy(self.data)
        data['permission_api'] = self.api
        self.assertDictEqual(self.permission.__dict__, data)

class TestPermissionApi(TestCase):
    def setUp(self):
        self.api = AirApi('http://test/api/', 'v1')
        self.permission = sdk.PermissionApi(self.api)

    def test_init(self):
        self.assertEqual(self.permission.api, self.api)
        self.assertEqual(self.permission.url, self.api.api_url + '/permission/')

    @requests_mock.Mocker()
    def test_create_permission(self, mock_requests):
        data = {'id': '123'}
        mock_requests.post(self.permission.url, status_code=201, json=data)
        permission, payload = self.permission.create_permission('foo@bar.com', simulation='foo')
        self.assertEqual(permission.id, '123')
        self.assertEqual(payload, data)

    def test_create_permission_missing_args(self):
        with pytest.raises(ValueError) as err:
            self.permission.create_permission('foo@bar.com')
            self.assertEqual(err.value, 'Creating a permission requires either a `simulation` ' + \
                                        'or `topology` argument')

    @requests_mock.Mocker()
    def test_create_permission_bad_code(self, mock_requests):
        mock_requests.post(self.permission.url, status_code=400)
        with pytest.raises(sdk.exceptions.AirUnexpectedResponse) as err:
            self.permission.create_permission('foo@bar.com', simulation='foo')
            self.assertEqual(err.value, 400)

    @requests_mock.Mocker()
    def test_create_permission_bad_json(self, mock_requests):
        mock_requests.post(self.permission.url, status_code=201, text='foo')
        with pytest.raises(sdk.exceptions.AirUnexpectedResponse) as err:
            self.permission.create_permission('foo@bar.com', simulation='foo')
            self.assertEqual(err.value, 'foo')
