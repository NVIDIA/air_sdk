"""
Tests for node.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring

from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock
import requests_mock
from cumulus_air_sdk import AirApi
import cumulus_air_sdk.air_sdk as sdk

class TestNode(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.api.api = MagicMock()
        self.data = {'url': 'http://test/api/v1/node/abc', 'id': 'abc', 'name': 'node1',
                     'os': 'def', 'memory': 1, 'storage': 2, 'cpu': 3,
                     'interfaces': [{'int1': 'foo'}], 'topology': 'xyz'}
        self.node = sdk.node.Node(self.api, **self.data)

    def test_init(self):
        self.assertEqual(self.node.node_api, self.api)
        data = deepcopy(self.data)
        data['node_api'] = self.api
        self.assertDictEqual(self.node.__dict__, data)

class TestNodeApi(TestCase):
    def setUp(self):
        self.api = AirApi('http://test/api/', 'v1')
        self.node = sdk.NodeApi(self.api)

    def test_init(self):
        self.assertEqual(self.node.api, self.api)
        self.assertEqual(self.node.url, self.api.api_url + '/node/')

    @requests_mock.Mocker()
    def test_get_nodes(self, mock_requests):
        nodes = [{'id': 'foo'}]
        mock_requests.get(self.node.url, json=nodes)
        res = self.node.get_nodes()
        self.assertListEqual(res, nodes)

    @requests_mock.Mocker()
    def test_get_nodes_by_sim(self, mock_requests):
        nodes = [{'id': 'foo'}]
        mock_requests.get(self.node.url + '?simulation=xyz', json=nodes)
        res = self.node.get_nodes('xyz')
        self.assertListEqual(res, nodes)
