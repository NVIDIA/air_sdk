# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for topology.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,unused-argument
import io
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import topology

class TestTopology(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.api.url = 'http://testserver/api/'
        self.model = topology.Topology(self.api)
        self.model.id = 'abc123'
        self.model.name = 'test'

    def test_init_(self):
        self.assertTrue(self.model._deletable)
        self.assertTrue(self.model._updatable)
        self.assertListEqual(topology.Topology._ignored_update_fields, ['links', 'nodes'])

    def test_repr(self):
        self.assertEqual(str(self.model), f'<Topology {self.model.name} {self.model.id}>')

    def test_add_permission(self):
        res = self.model.add_permission('me@test.com', foo='bar')
        self.api.client.permissions.create.assert_called_with(email='me@test.com',
                                                              topology=self.model.id, foo='bar')
        self.assertEqual(res, self.api.client.permissions.create.return_value)

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))


class TestTopologyApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = topology.TopologyApi(self.client)

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/topology/')

    @patch('air_sdk.air_sdk.topology.TopologyApi.list')
    def test_get_topologies(self, mock_list):
        self.assertEqual(self.api.get_topologies(), mock_list.return_value)

    @patch('air_sdk.air_sdk.topology.TopologyApi.create')
    def test_create_topology(self, mock_create):
        res = self.api.create_topology(dot='test')
        mock_create.assert_called_with(dot='test', json=None)
        self.assertEqual(res, mock_create.return_value)

    @patch('air_sdk.air_sdk.topology.TopologyApi.get')
    def test_update_topology(self, mock_get):
        self.api.update_topology('abc123', {'foo': 'bar'})
        mock_get.assert_called_with('abc123')
        mock_get.return_value.update.assert_called_with(foo='bar')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get(self, mock_raise):
        self.client.get.return_value.json.return_value = {'test': 'success'}
        res = self.api.get('abc123', foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/topology/abc123/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, topology.Topology)
        self.assertEqual(res.test, 'success')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list(self, mock_raise):
        self.client.get.return_value.json.return_value = [{'id': 'abc'}, {'id': 'xyz'}]
        res = self.api.list(foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/topology/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value, data_type=list)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], topology.Topology)
        self.assertEqual(res[0].id, 'abc')
        self.assertEqual(res[1].id, 'xyz')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create_json(self, mock_raise):
        self.client.post.return_value.json.return_value = {'id': 'abc'}
        res = self.api.create(json={'foo': 'bar'})
        self.client.post.assert_called_with(f'{self.client.api_url}/topology/',
                                            json={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        self.assertIsInstance(res, topology.Topology)
        self.assertEqual(res.id, 'abc')

    @patch('os.path.isfile', return_value=False)
    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create_dot(self, mock_raise, *args):
        self.client.post.return_value.json.return_value = {'id': 'abc'}
        res = self.api.create(dot='test')
        self.client.post.assert_called_with(f'{self.client.api_url}/topology/', data=b'test',
                                            headers={'Content-type': 'text/vnd.graphviz'})
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        self.assertIsInstance(res, topology.Topology)
        self.assertEqual(res.id, 'abc')

    @patch('os.path.isfile', return_value=False)
    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create_dot_file(self, mock_raise, *args):
        self.client.post.return_value.json.return_value = {'id': 'abc'}
        mock_file = MagicMock(spec=io.IOBase)
        res = self.api.create(dot=mock_file)
        self.client.post.assert_called_with(f'{self.client.api_url}/topology/', data=mock_file,
                                            headers={'Content-type': 'text/vnd.graphviz'})
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        self.assertIsInstance(res, topology.Topology)
        self.assertEqual(res.id, 'abc')

    @patch('builtins.open')
    @patch('os.path.isfile', return_value=True)
    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create_dot_file_path(self, mock_raise, mock_isfile, mock_open):
        self.client.post.return_value.json.return_value = {'id': 'abc'}
        file_path = '/tmp/topo.dot'
        res = self.api.create(dot=file_path)
        self.client.post.assert_called_with(f'{self.client.api_url}/topology/',
                                            data=mock_open.return_value.read.return_value,
                                            headers={'Content-type': 'text/vnd.graphviz'})
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        self.assertIsInstance(res, topology.Topology)
        self.assertEqual(res.id, 'abc')
        mock_isfile.assert_called_once_with(file_path)
        mock_open.assert_called_once_with(file_path, 'r')

    def test_create_required_kwargs(self):
        with self.assertRaises(AttributeError) as err:
            self.api.create()
        self.assertTrue('requires one of the following: (\'json\', \'dot\')' in str(err.exception))
