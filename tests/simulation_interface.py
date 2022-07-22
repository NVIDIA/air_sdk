# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for simulation_interface.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,unused-argument
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import simulation_interface

class TestSimulationInterface(TestCase):
    def setUp(self):
        self.model = simulation_interface.SimulationInterface(MagicMock())
        self.model.id = 'abc123'

    def test_init_(self):
        self.assertFalse(self.model._deletable)
        self.assertTrue(self.model._updatable)

    def test_repr(self):
        self.assertEqual(str(self.model), f'<SimulationInterface {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))


class TestSimulationInterfaceApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = simulation_interface.SimulationInterfaceApi(self.client)

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/simulation-interface/')

    @patch('air_sdk.air_sdk.simulation_interface.SimulationInterfaceApi.list')
    def test_get_simulation_interfaces(self, mock_list):
        res = self.api.get_simulation_interfaces('abc123', 'xyz123')
        mock_list.assert_called_with(simulation='abc123', original='xyz123')
        self.assertEqual(res, mock_list.return_value)

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get(self, mock_raise):
        self.client.get.return_value.json.return_value = {'test': 'success'}
        res = self.api.get('abc123', foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/simulation-interface/abc123/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, simulation_interface.SimulationInterface)
        self.assertEqual(res.test, 'success')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list(self, mock_raise):
        self.client.get.return_value.json.return_value = [{'id': 'abc'}, {'id': 'xyz'}]
        res = self.api.list(foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/simulation-interface/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value, data_type=list)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], simulation_interface.SimulationInterface)
        self.assertEqual(res[0].id, 'abc')
        self.assertEqual(res[1].id, 'xyz')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list_interface(self, mock_raise):
        self.api.list(interface='test')
        self.client.get.assert_called_with(f'{self.client.api_url}/simulation-interface/',
                                           params={'original': 'test'})
