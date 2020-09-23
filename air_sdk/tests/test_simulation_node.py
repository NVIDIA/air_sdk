"""
Tests for topology.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring

from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock
import cumulus_air_sdk.air_sdk as sdk

class TestSimulationNode(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.api.api = MagicMock()
        self.data = {'id': 'abc', 'url': 'http://testserver/api/v1/simulation-node/abc/',
                     'name': 'simnode1', 'simulation': 'def', 'original': 'xyz',
                     'interfaces': ['123', '456'], 'console_port': 12345, 'state': 'RUNNING',
                     'worker': 'abxc123', 'serial_port': 23456, 'console_username': 'foo',
                     'console_password': 'bar', 'console_url': 'http://testserver/api/v1/console'}
        self.simulation_node = sdk.simulation_node.SimulationNode(self.api, **self.data)

    def test_init(self):
        data = deepcopy(self.data)
        data['simulation_node_api'] = self.api
        self.assertDictEqual(self.simulation_node.__dict__, data)

    def test_update(self):
        self.simulation_node.update(serial_port=9999)
        data = deepcopy(self.data)
        data['serial_port'] = 9999
        self.api.update_simulation_node.assert_called_with(self.simulation_node.id, data)

class TestSimulationNodeApi(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.api.api_url = 'http://testserver'
        self.simulation_node = sdk.SimulationNodeApi(self.api)

    def test_init(self):
        self.assertEqual(self.simulation_node.api, self.api)
        self.assertEqual(self.simulation_node.url, self.api.api_url + '/simulation-node/')

    def test_update_simulation_node(self):
        data = {'console_password': 'wings'}
        self.api.put.return_value.status_code = 200
        self.simulation_node.update_simulation_node('abc', data)
        self.api.put.assert_called_with('http://testserver/simulation-node/abc/', json=data)

    def test_update_simulation_node_bad_status(self):
        self.api.put.return_value.status_code = 400
        self.api.put.return_value.data = 'test error'
        with self.assertRaises(sdk.exceptions.AirUnexpectedResponse) as err:
            self.simulation_node.update_simulation_node('abc', {})
        message = 'Received an unexpected response from the Cumulus AIR API: test error'
        self.assertEqual(err.exception.message, message)
        self.assertEqual(err.exception.status_code, 400)

    def test_get_simulation_nodes(self):
        self.api.get.return_value.status_code = 200
        self.api.get.return_value.json.return_value = 'test'
        res = self.simulation_node.get_simulation_nodes(simulation='12345')
        self.api.get.assert_called_with('http://testserver/simulation-node/?&simulation=12345')
        self.assertEqual(res, 'test')

    def test_get_simulation_nodes_bad_status(self):
        self.api.get.return_value.status_code = 400
        self.api.get.return_value.data = 'test error'
        with self.assertRaises(sdk.exceptions.AirUnexpectedResponse) as err:
            self.simulation_node.get_simulation_nodes(simulation='12345')
        message = 'Received an unexpected response from the Cumulus AIR API: test error'
        self.assertEqual(err.exception.message, message)
        self.assertEqual(err.exception.status_code, 400)
