"""
Tests for worker.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,unused-argument
from copy import deepcopy

from unittest import TestCase
from unittest.mock import MagicMock
import cumulus_air_sdk.air_sdk as sdk

class TestWorker(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.data = {'url': 'http://testserver/worker/1/', 'id': '123', 'cpu': 1, 'memory': 2,
                     'storage': 3, 'ip_address': '1.2.3.4', 'port_range': '100-200',
                     'region': '456', 'available': True, 'fqdn': 'worker1.test'}
        self.worker = sdk.worker.Worker(self.api, **self.data)

    def test_init(self):
        data = deepcopy(self.data)
        data['worker_api'] = self.api
        self.assertDictEqual(self.worker.__dict__, data)

    def test_set_available(self):
        self.worker.set_available(True)
        self.api.update_worker.assert_called_with(self.worker.id, **self.worker.__dict__)

class TestWorkerApi(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.api.api_url = 'http://testserver/api'
        self.worker = sdk.worker.WorkerApi(self.api)

    def test_init(self):
        self.assertEqual(self.worker.api, self.api)
        self.assertEqual(self.worker.url, 'http://testserver/api/worker/')

    def test_get_workers(self):
        self.api.get.return_value.json.return_value = [{'id': '1'}, {'id': '2'}]
        res = self.worker.get_workers()
        self.api.get.assert_called_with(f'{self.worker.url}?')
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].id, '1')
        self.assertEqual(res[1].id, '2')

    def test_get_workers_filter(self):
        self.worker.get_workers(name='test', id='2')
        self.api.get.assert_called_with(f'{self.worker.url}?&name=test&id=2')

    def test_update_worker(self):
        self.api.put.return_value.json.return_value = {'id': 'foo'}
        res = self.worker.update_worker('123', name='test')
        self.api.put.assert_called_with(f'{self.worker.url}123/', {'id': '123', 'name': 'test'})
        self.assertEqual(res.id, 'foo')
