# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for simulation_node.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,unused-argument
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import simulation_node

class TestSimulationNode(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.api.url = 'http://testserver/api/'
        self.model = simulation_node.SimulationNode(self.api)
        self.model.id = 'abc123'

    def test_init_(self):
        self.assertFalse(self.model._deletable)
        self.assertTrue(self.model._updatable)

    def test_repr(self):
        self.assertEqual(str(self.model), f'<SimulationNode {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))


    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create_instructions(self, mock_raise):
        res = self.model.create_instructions(executor='shell', data='echo')
        self.api.client.post.assert_called_with(f'{self.api.url}abc123/instructions/',
                                                json={'executor': 'shell', 'data': 'echo'})
        mock_raise.assert_called_with(self.api.client.post.return_value, status_code=201,
                                      data_type=str)
        self.assertEqual(res, {'id': self.api.client.post.return_value.json.return_value})

    def test_create_instructions_required_kwargs(self):
        with self.assertRaises(AttributeError) as err:
            self.model.create_instructions(executor='shell')
        self.assertTrue('requires data' in str(err.exception))
        with self.assertRaises(AttributeError) as err:
            self.model.create_instructions(data='foo')
        self.assertTrue('requires executor' in str(err.exception))

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create_instructions_list(self, mock_raise):
        self.model.create_instructions(executor='shell', data=['line1', 'line2'])
        self.api.client.post.assert_called_with(f'{self.api.url}abc123/instructions/',
                                                json={'executor': 'shell', 'data': 'line1\nline2'})

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list_instructions(self, mock_raise):
        res = self.model.list_instructions(foo='bar')
        self.api.client.get.assert_called_with(f'{self.api.url}{self.model.id}/instructions/',
                                               params={'foo': 'bar'})
        mock_raise.assert_called_with(self.api.client.get.return_value, data_type=list)
        self.assertEqual(res, self.api.client.get.return_value.json.return_value)

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_delete_instructions(self, mock_raise):
        self.model.delete_instructions()
        self.api.client.delete.assert_called_with(f'{self.api.url}{self.model.id}/instructions/')
        mock_raise.assert_called_with(self.api.client.delete.return_value, status_code=204,
                                      data_type=None)

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_control(self, mock_raise):
        res = self.model.control(action='test')
        self.api.client.post.assert_called_with(f'{self.api.url}{self.model.id}/control/',
                                                json={'action': 'test'})
        mock_raise.assert_called_with(self.api.client.post.return_value)
        self.assertEqual(res, self.api.client.post.return_value.json.return_value)

    def test_control_required_kwargs(self):
        with self.assertRaises(AttributeError) as err:
            self.model.control()
        self.assertTrue('requires action' in str(err.exception))

    @patch('air_sdk.air_sdk.simulation_node.SimulationNode.control')
    def test_rebuild(self, mock_control):
        self.model.rebuild(foo='bar')
        mock_control.assert_called_with(action='rebuild', foo='bar')

    @patch('air_sdk.air_sdk.simulation_node.SimulationNode.control')
    def test_reset(self, mock_control):
        self.model.reset(foo='bar')
        mock_control.assert_called_with(action='reset', foo='bar')

class TestSimulationNodeApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = simulation_node.SimulationNodeApi(self.client)

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/simulation-node/')

    @patch('air_sdk.air_sdk.simulation_node.SimulationNodeApi.get')
    def test_update_simulation_node(self, mock_get):
        self.api.update_simulation_node('abc123', {'foo': 'bar'})
        mock_get.assert_called_with('abc123')
        mock_get.return_value.update.assert_called_with(foo='bar')

    @patch('air_sdk.air_sdk.simulation_node.SimulationNodeApi.list')
    def test_get_simulation_nodes(self, mock_list):
        res = self.api.get_simulation_nodes(foo='bar')
        mock_list.assert_called_with(foo='bar')
        self.assertEqual(res, mock_list.return_value)

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get(self, mock_raise):
        self.client.get.return_value.json.return_value = {'test': 'success'}
        res = self.api.get('abc123', foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/simulation-node/abc123/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, simulation_node.SimulationNode)
        self.assertEqual(res.test, 'success')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list(self, mock_raise):
        self.client.get.return_value.json.return_value = [{'id': 'abc'}, {'id': 'xyz'}]
        res = self.api.list(foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/simulation-node/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value, data_type=list)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], simulation_node.SimulationNode)
        self.assertEqual(res[0].id, 'abc')
        self.assertEqual(res[1].id, 'xyz')
