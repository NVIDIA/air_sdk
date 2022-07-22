# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for node.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,unused-argument
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import node

class TestNode(TestCase):
    def setUp(self):
        self.model = node.Node(MagicMock())
        self.model.id = 'abc123'
        self.model.name = 'server'

    def test_init_(self):
        self.assertTrue(self.model._deletable)
        self.assertTrue(self.model._updatable)
        self.assertListEqual(self.model._ignored_update_fields, ['interfaces'])

    def test_repr(self):
        self.assertEqual(str(self.model), f'<Node {self.model.name} {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))

class TestNodeApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = node.NodeApi(self.client)

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/node/')

    @patch('air_sdk.air_sdk.node.NodeApi.list')
    def test_get_nodes(self, mock_list):
        res = self.api.get_nodes(simulation_id='foo')
        mock_list.assert_called_with(simulation='foo')
        self.assertEqual(res, mock_list.return_value)

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get(self, mock_raise):
        self.client.get.return_value.json.return_value = {'test': 'success'}
        res = self.api.get('abc123', foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/node/abc123/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, node.Node)
        self.assertEqual(res.test, 'success')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get_simulation_id(self, mock_raise):
        self.client.get.return_value.json.return_value = {'test': 'success'}
        self.api.get('abc123', simulation_id='xyz123')
        self.client.get.assert_called_with(f'{self.client.api_url}/node/abc123/',
                                           params={'simulation': 'xyz123'})

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list(self, mock_raise):
        self.client.get.return_value.json.return_value = [{'id': 'abc'}, {'id': 'xyz'}]
        res = self.api.list(foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/node/', params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value, data_type=list)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], node.Node)
        self.assertEqual(res[0].id, 'abc')
        self.assertEqual(res[1].id, 'xyz')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create(self, mock_raise):
        self.client.post.return_value.json.return_value = {'id': 'abc'}
        res = self.api.create(topology='abc123', name='test')
        self.client.post.assert_called_with(f'{self.client.api_url}/node/',
                                            json={'topology': 'abc123', 'name': 'test'})
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        self.assertIsInstance(res, node.Node)
        self.assertEqual(res.id, 'abc')

    def test_create_required_kwargs(self):
        with self.assertRaises(AttributeError) as err:
            self.api.create(name='test')
        self.assertTrue('requires topology' in str(err.exception))
        with self.assertRaises(AttributeError) as err:
            self.api.create(topology='abc123')
        self.assertTrue('requires name' in str(err.exception))
