"""
Tests for service.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring

from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock
import pytest
import requests_mock
from cumulus_air_sdk import AirApi
import cumulus_air_sdk.air_sdk as sdk

class TestService(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.data = {'url': 'http://test/api/v1/service/abc', 'id': 'abc',
                     'name': 'ssh oob-mgmt-server', 'simulation': 'foo', 'interface': 'def',
                     'dest_port': 22, 'src_port': 12345, 'link': 'http://test:$', 'host': 'test'}
        self.service = sdk.service.Service(self.api, **self.data)

    def test_init(self):
        self.assertEqual(self.service.service_api, self.api)
        data = deepcopy(self.data)
        data['service_api'] = self.api
        self.assertDictEqual(self.service.__dict__, data)

class TestServiceApi(TestCase):
    def setUp(self):
        self.api = AirApi('http://test/api/', 'v1')
        self.service = sdk.ServiceApi(self.api)

    def test_init(self):
        self.assertEqual(self.service.api, self.api)
        self.assertEqual(self.service.url, self.api.api_url + '/service/')

    @requests_mock.Mocker()
    def test_get_services(self, mock_requests):
        payload = [{'id': 1}]
        mock_requests.get(self.service.url, json=payload)
        res = self.service.get_services()
        self.assertListEqual(res, payload)

    @requests_mock.Mocker()
    def test_get_service(self, mock_requests):
        mock_requests.get(f'{self.service.url}abc/', json={'id': 'abc'})
        res = self.service.get_service('abc')
        self.assertEqual(res.id, 'abc')

    @requests_mock.Mocker()
    def test_create_service(self, mock_requests):
        self.api.node = MagicMock()
        nodes = [
            {'name': 'foo', 'interfaces': [{'name': 'foo', 'id': 1}]},
            {'name': 'oob-mgmt-server', 'interfaces': [{'name': 'eth0', 'id': 2}]}
        ]
        self.api.node.get_nodes = MagicMock(return_value=nodes)
        self.api.simulation_interface.get_simulation_interfaces = \
            MagicMock(return_value=[{'id': '999'}])
        mock_requests.post(self.service.url, status_code=201, json={'id': 'xyz'})
        service, payload = self.service.create_service('abc', 'ssh oob-mgmt-server',
                                                       'oob-mgmt-server:eth0', 22, test='new')
        self.assertEqual(service.id, 'xyz')
        self.assertEqual(payload, {'id': 'xyz'})

    def test_create_service_bad_format(self):
        with pytest.raises(ValueError) as err:
            self.service.create_service('abc', 'ssh oob-mgmt-server', 'foo', 22)
            self.assertEqual(err.value,
                             '`interface` must be in the format of "node_name:interface_name"')

    def test_create_service_no_interface(self):
        self.api.node = MagicMock()
        nodes = [
            {'name': 'foo', 'interfaces': [{'name': 'foo', 'id': 1}]},
            {'name': 'foo2', 'interfaces': [{'name': 'eth0', 'id': 2}]}
        ]
        self.api.node.get_nodes = MagicMock(return_value=nodes)
        with pytest.raises(ValueError) as err:
            self.service.create_service('abc', 'ssh oob-mgmt-server', 'oob-mgmt-server:eth0', 22)
            self.assertEqual(err.value, 'Interface oob-mgmt-server:eth0 not does not exist')

    def test_create_service_no_simint(self):
        self.api.node = MagicMock()
        nodes = [
            {'name': 'foo', 'interfaces': [{'name': 'foo', 'id': 1}]},
            {'name': 'oob-mgmt-server', 'interfaces': [{'name': 'eth0', 'id': 2}]}
        ]
        self.api.node.get_nodes = MagicMock(return_value=nodes)
        self.api.simulation_interface.get_simulation_interfaces = \
            MagicMock(return_value=[])
        with pytest.raises(sdk.exceptions.AirUnexpectedResponse) as err:
            self.service.create_service('abc', 'ssh oob-mgmt-server', 'oob-mgmt-server:eth0', 22)
            self.assertEqual(err.value, [])

    @requests_mock.Mocker()
    def test_create_service_bad_code(self, mock_requests):
        self.api.node = MagicMock()
        nodes = [
            {'name': 'foo', 'interfaces': [{'name': 'foo', 'id': '1'}]},
            {'name': 'oob-mgmt-server', 'interfaces': [{'name': 'eth0', 'id': '2'}]}
        ]
        self.api.node.get_nodes = MagicMock(return_value=nodes)
        self.api.simulation_interface.get_simulation_interfaces = \
            MagicMock(return_value=[{'id': 'xyz'}])
        mock_requests.post(self.service.url, status_code=400)
        with pytest.raises(sdk.exceptions.AirUnexpectedResponse) as err:
            self.service.create_service('abc', 'ssh oob-mgmt-server', 'oob-mgmt-server:eth0', 22)
            self.assertEqual(err.value, 400)

    @requests_mock.Mocker()
    def test_create_service_bad_json(self, mock_requests):
        self.api.node = MagicMock()
        nodes = [
            {'name': 'foo', 'interfaces': [{'name': 'foo', 'id': '1'}]},
            {'name': 'oob-mgmt-server', 'interfaces': [{'name': 'eth0', 'id': '2'}]}
        ]
        self.api.node.get_nodes = MagicMock(return_value=nodes)
        self.api.simulation_interface.get_simulation_interfaces = \
            MagicMock(return_value=[{'id': 'xyz'}])
        mock_requests.post(self.service.url, status_code=201, text='foo')
        with pytest.raises(sdk.exceptions.AirUnexpectedResponse) as err:
            self.service.create_service('abc', 'ssh oob-mgmt-server', 'oob-mgmt-server:eth0', 22)
            self.assertEqual(err.value, 'foo')
