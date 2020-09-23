"""
Tests for topology.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring

from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock
import cumulus_air_sdk.air_sdk as sdk

class TestTopology(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.api.api = MagicMock()
        self.data = {'id': 'abc', 'url': 'http://testserver/api/v1/topology/abc/', 'name': 'topo1',
                     'organization': 'foo', 'documentation': 'my docs',
                     'diagram_url': 'http://testserver/diagram'}
        self.topology = sdk.topology.Topology(self.api, **self.data)

    def test_init(self):
        data = deepcopy(self.data)
        data['topology_api'] = self.api
        self.assertDictEqual(self.topology.__dict__, data)

    def test_update(self):
        self.topology.update(documentation='test')
        data = deepcopy(self.data)
        data['documentation'] = 'test'
        self.api.update_topology.assert_called_with(self.topology.id, data)

    def test_add_permission(self):
        self.api.api.permission = MagicMock()
        self.api.api.permission.create_permission = MagicMock()
        self.topology.add_permission('foo@bar.com', foo='bar')
        self.api.api.permission.create_permission.assert_called_with('foo@bar.com',
                                                                     topology=self.data['id'],
                                                                     foo='bar')
class TestTopologyApi(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.api.api_url = 'http://testserver'
        self.topology = sdk.TopologyApi(self.api)

    def test_get_topologies(self):
        self.api.get.return_value.json.return_value = ['foo', 'bar']
        res = self.topology.get_topologies()
        self.api.get.assert_called_with('http://testserver/topology/')
        self.assertEqual(res, ['foo', 'bar'])

    def test_get_topology(self):
        # TODO
        self.topology.get_topology()

    def test_create_topology_json(self):
        self.api.post.return_value.status_code = 201
        self.api.post.return_value.json.return_value = {'name': 'foo'}
        res, json = self.topology.create_topology(json={'foo': 'bar'})
        self.api.post.assert_called_with(self.topology.url, json={'foo': 'bar'})
        self.assertEqual(res.name, 'foo')
        self.assertDictEqual(json, {'name': 'foo'})

    def test_create_topology_dot(self):
        self.api.post.return_value.status_code = 201
        self.api.post.return_value.json.return_value = {'name': 'foo'}
        res, json = self.topology.create_topology(dot='foobar')
        self.api.post.assert_called_with(self.topology.url, data=b'foobar',
                                         headers={'Content-type': 'text/vnd.graphviz'})
        self.assertEqual(res.name, 'foo')
        self.assertDictEqual(json, {'name': 'foo'})

    def test_create_topology_missing_args(self):
        with self.assertRaises(ValueError) as err:
            self.topology.create_topology()
        self.assertEqual(str(err.exception),
                         'TopologyApi.create_topology requires a `json` or `dot` argument')

    def test_create_topology_bad_response(self):
        self.api.post.return_value.status_code = 400
        self.api.post.return_value.data = 'test error'
        with self.assertRaises(sdk.exceptions.AirUnexpectedResponse) as err:
            self.topology.create_topology(dot='foobar')
        self.assertEqual(err.exception.message,
                         'Received an unexpected response from the Cumulus AIR API: test error')
        self.assertEqual(err.exception.status_code, 400)

    def test_update_topology(self):
        self.api.put.return_value.status_code = 200
        data = {'foo': 'bar'}
        self.topology.update_topology('abc', data)
        self.api.put.assert_called_with('http://testserver/topology/abc/', json=data)

    def test_update_topology_bad_status(self):
        self.api.put.return_value.status_code = 400
        self.api.put.return_value.data = 'test error'
        data = {'foo': 'bar'}
        with self.assertRaises(sdk.exceptions.AirUnexpectedResponse) as err:
            self.topology.update_topology('abc', data)
        self.assertEqual(err.exception.message,
                         'Received an unexpected response from the Cumulus AIR API: test error')
        self.assertEqual(err.exception.status_code, 400)
