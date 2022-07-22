# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for service.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,unused-argument
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import service
from ..air_sdk.air_model import AirModel

class TestService(TestCase):
    def setUp(self):
        self.model = service.Service(MagicMock())
        self.model.id = 'abc123'
        self.model.name = 'http'

    def test_init_(self):
        self.assertTrue(self.model._deletable)
        self.assertTrue(self.model._updatable)

    def test_repr(self):
        self.assertEqual(str(self.model), f'<Service {self.model.name} {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))


class TestServiceApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = service.ServiceApi(self.client)

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/service/')

    @patch('air_sdk.air_sdk.service.ServiceApi.list')
    def test_get_services(self, mock_list):
        self.assertEqual(self.api.get_services(), mock_list.return_value)

    @patch('air_sdk.air_sdk.service.ServiceApi.get')
    def test_get_service(self, mock_get):
        res = self.api.get_service('abc123')
        mock_get.assert_called_with('abc123')
        self.assertEqual(res, mock_get.return_value)

    @patch('air_sdk.air_sdk.service.ServiceApi.create')
    def test_create_service(self, mock_create):
        res = self.api.create_service('abc123', 'test', 'intf', 22, foo='bar')
        mock_create.assert_called_with(simulation='abc123', name='test', interface='intf',
                                       dest_port=22, foo='bar')
        self.assertEqual(res, mock_create.return_value)

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get(self, mock_raise):
        self.client.get.return_value.json.return_value = {'test': 'success'}
        res = self.api.get('abc123', foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/service/abc123/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, service.Service)
        self.assertEqual(res.test, 'success')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list(self, mock_raise):
        self.client.get.return_value.json.return_value = [{'id': 'abc'}, {'id': 'xyz'}]
        res = self.api.list(foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/service/', params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value, data_type=list)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], service.Service)
        self.assertEqual(res[0].id, 'abc')
        self.assertEqual(res[1].id, 'xyz')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    @patch('air_sdk.air_sdk.service.ServiceApi._resolve_interface')
    def test_create(self, mock_resolve, mock_raise):
        sim = AirModel(MagicMock(), id='xyz123')
        self.client.post.return_value.json.return_value = {'id': 'abc'}
        res = self.api.create(name='abc123', simulation=sim, interface='test:eth0')
        mock_resolve.assert_called_with('test:eth0', sim)
        self.client.post.assert_called_with(f'{self.client.api_url}/service/',
                                            json={'name': 'abc123', 'simulation': sim,
                                                  'interface': mock_resolve.return_value})
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        self.assertIsInstance(res, service.Service)
        self.assertEqual(res.id, 'abc')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    @patch('air_sdk.air_sdk.service.ServiceApi._resolve_interface')
    def test_create_id(self, mock_resolve, mock_raise):
        self.client.post.return_value.json.return_value = {'id': 'abc'}
        self.api.create(name='abc123', simulation='xyz123', interface='test123')
        mock_resolve.assert_not_called()
        self.client.post.assert_called_with(f'{self.client.api_url}/service/',
                                            json={'name': 'abc123', 'simulation': 'xyz123',
                                                  'interface': 'test123'})

    def test_create_required_kwargs(self):
        with self.assertRaises(AttributeError) as err:
            self.api.create(simulation='abc123', interface='xyz123')
        self.assertTrue('requires name' in str(err.exception))
        with self.assertRaises(AttributeError) as err:
            self.api.create(name='test', interface='xyz123')
        self.assertTrue('requires simulation' in str(err.exception))
        with self.assertRaises(AttributeError) as err:
            self.api.create(name='test', simulation='xyz123')
        self.assertTrue('requires interface' in str(err.exception))

    def test_resolve_interface(self):
        intf1 = MagicMock()
        intf1.name = 'eth0'
        intf2 = MagicMock()
        intf2.name = 'eth1'
        node1 = MagicMock()
        node1.name = 'server'
        node1.interfaces = [intf1, intf2]
        node2 = MagicMock()
        node2.name = 'foo'
        node2.interfaces = [intf1, intf2]
        self.client.nodes.list.return_value = [node1, node2]
        mock_simint = MagicMock()
        self.client.simulation_interfaces.list.return_value = [mock_simint]
        res = self.api._resolve_interface('server:eth0', 'abc123')
        self.client.nodes.list.assert_called_with(simulation='abc123')
        self.client.simulation_interfaces.list.assert_called_with(original=intf1,
                                                                  simulation='abc123')
        self.assertEqual(res, mock_simint)

    def test_resolve_interface_bad_input(self):
        with self.assertRaises(ValueError) as err:
            self.api._resolve_interface('eth0', 'abc123')
        self.assertEqual(str(err.exception),
                         '`interface` must be an Interface object or in the format of ' + \
                         '"node_name:interface_name"')

    def test_resolve_interface_not_found(self):
        with self.assertRaises(ValueError) as err:
            self.api._resolve_interface('server:eth0', 'abc123')
        self.assertEqual(str(err.exception), 'Interface server:eth0 does not exist')
