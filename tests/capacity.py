# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for capacity.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,unused-argument
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import capacity
from ..air_sdk.simulation import Simulation

class TestCapacity(TestCase):
    def setUp(self):
        self.model = capacity.Capacity(MagicMock())
        self.model.copies = 30

    def test_init_(self):
        self.assertFalse(self.model._deletable)
        self.assertFalse(self.model._updatable)

    def test_repr(self):
        self.assertEqual(str(self.model), f'<Capacity {self.model.copies}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))

class TestCapacityApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = capacity.CapacityApi(self.client)

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/capacity/')

    @patch('air_sdk.air_sdk.capacity.CapacityApi.get')
    def test_get_capacity_by_sim(self, mock_get):
        mock_sim = MagicMock()
        res = self.api.get_capacity(mock_sim)
        mock_get.assert_called_with(simulation_id=mock_sim.id)
        self.assertEqual(res, mock_get.return_value)

    @patch('air_sdk.air_sdk.capacity.CapacityApi.get')
    def test_get_capacity_by_id(self, mock_get):
        res = self.api.get_capacity(simulation_id='abc123')
        mock_get.assert_called_with(simulation_id='abc123')
        self.assertEqual(res, mock_get.return_value)

    def test_get_capacity_missing_param(self):
        with self.assertRaises(ValueError) as err:
            self.api.get_capacity()
        self.assertEqual(str(err.exception), 'Must pass a simulation or simulation_id argument')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get(self, mock_raise):
        self.client.get.return_value.json.return_value = {'test': 'success'}
        res = self.api.get('abc123', foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/capacity/abc123/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, capacity.Capacity)
        self.assertEqual(res.test, 'success')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get_simulation(self, mock_raise):
        sim = Simulation(MagicMock())
        sim.id = 'abc123'
        self.api.get(sim)
        self.client.get.assert_called_with(f'{self.client.api_url}/capacity/abc123/', params={})
