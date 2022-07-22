# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for worker.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import worker

class TestWorker(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.model = worker.Worker(self.api)
        self.model.fqdn = 'test.test'
        self.model.id = 'abc123'

    def test_init_(self):
        self.assertFalse(self.model._deletable)
        self.assertTrue(self.model._updatable)

    def test_repr(self):
        self.assertEqual(str(self.model), f'<Worker {self.model.fqdn} {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))

    @patch('air_sdk.air_sdk.air_model.AirModel._patch')
    def test_set_available(self, mock_patch):
        self.model.available = False
        self.model.set_available(True)
        self.assertTrue(self.model.available)
        mock_patch.assert_called()

class TestWorkerApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = worker.WorkerApi(self.client)

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/worker/')

    @patch('air_sdk.air_sdk.worker.WorkerApi.list')
    def test_get_workers(self, mock_list):
        res = self.api.get_workers(foo='bar')
        mock_list.assert_called_with(foo='bar')
        self.assertEqual(res, mock_list.return_value)

    @patch('air_sdk.air_sdk.worker.WorkerApi.get')
    def test_update_worker(self, mock_get):
        res = self.api.update_worker('abc123', foo='bar')
        mock_get.assert_called_with('abc123')
        mock_get.return_value.update.assert_called_with(foo='bar')
        self.assertEqual(res, mock_get.return_value.update.return_value)

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get(self, mock_raise):
        self.client.get.return_value.json.return_value = {'test': 'success'}
        res = self.api.get('abc123', foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/worker/abc123/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, worker.Worker)
        self.assertEqual(res.test, 'success')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list(self, mock_raise):
        self.client.get.return_value.json.return_value = [{'id': 'abc'}, {'id': 'xyz'}]
        res = self.api.list(foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/worker/', params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value, data_type=list)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], worker.Worker)
        self.assertEqual(res[0].id, 'abc')
        self.assertEqual(res[1].id, 'xyz')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create(self, mock_raise):
        self.client.post.return_value.json.return_value = {'id': 'abc'}
        res = self.api.create(cpu=1, memory=2, storage=3, ip_address='10.1.1.1', port_range='1-2',
                              username='foo', password='bar')
        self.client.post.assert_called_with(f'{self.client.api_url}/worker/',
                                            json={'cpu': 1, 'memory': 2, 'storage': 3,
                                                  'ip_address': '10.1.1.1', 'port_range': '1-2',
                                                  'username': 'foo', 'password': 'bar'})
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        self.assertIsInstance(res, worker.Worker)
        self.assertEqual(res.id, 'abc')

    def test_create_required_kwargs(self):
        with self.assertRaises(AttributeError) as err:
            self.api.create(memory=2, storage=3, ip_address='10.1.1.1', port_range='1-2',
                            username='foo', password='bar')
        self.assertTrue('requires cpu' in str(err.exception))
        with self.assertRaises(AttributeError) as err:
            self.api.create(cpu=1, storage=3, ip_address='10.1.1.1', port_range='1-2',
                            username='foo', password='bar')
        self.assertTrue('requires memory' in str(err.exception))
        with self.assertRaises(AttributeError) as err:
            self.api.create(cpu=1, memory=2, ip_address='10.1.1.1', port_range='1-2',
                            username='foo', password='bar')
        self.assertTrue('requires storage' in str(err.exception))
        with self.assertRaises(AttributeError) as err:
            self.api.create(cpu=1, memory=2, storage=3, port_range='1-2', username='foo',
                            password='bar')
        self.assertTrue('requires ip_address' in str(err.exception))
        with self.assertRaises(AttributeError) as err:
            self.api.create(cpu=1, memory=2, storage=3, ip_address='10.1.1.1', username='foo',
                            password='bar')
        self.assertTrue('requires port_range' in str(err.exception))
        with self.assertRaises(AttributeError) as err:
            self.api.create(cpu=1, memory=2, storage=3, ip_address='10.1.1.1', port_range='1-2',
                            password='bar')
        self.assertTrue('requires username' in str(err.exception))
        with self.assertRaises(AttributeError) as err:
            self.api.create(cpu=1, memory=2, storage=3, ip_address='10.1.1.1', port_range='1-2',
                            username='foo')
        self.assertTrue('requires password' in str(err.exception))
