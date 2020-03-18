"""
Tests for simulation_interface.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring

from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock
import requests_mock
from cumulus_air_sdk import AirApi
import cumulus_air_sdk.air_sdk as sdk

class TestSimulationInterface(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.data = {'url': 'http://test/api/v1/simulation-interface/abc', 'id': 'abc',
                     'node': 'def', 'original': 'xyz', 'link_up': True,
                     'services': [{'svc1': 'test'}], 'internal_ipv4': '1.2.3.4',
                     'prefix_ipv6': 'fd01:1::', 'full_ipv6': 'fd01:1:a:1',
                     'mac_address': 'de:ad:be:ef:ca:fe'}
        self.simulation_interface = sdk.simulation_interface.SimulationInterface(self.api,
                                                                                 **self.data)

    def test_init(self):
        self.assertEqual(self.simulation_interface.simulation_interface_api, self.api)
        data = deepcopy(self.data)
        data['simulation_interface_api'] = self.api
        self.assertDictEqual(self.simulation_interface.__dict__, data)

class TestSimulationInterfaceApi(TestCase):
    def setUp(self):
        self.api = AirApi('http://test/api/', 'v1')
        self.simulation_interface = sdk.SimulationInterfaceApi(self.api)

    def test_init(self):
        self.assertEqual(self.simulation_interface.api, self.api)
        self.assertEqual(self.simulation_interface.url, self.api.api_url + '/simulation-interface/')

    @requests_mock.Mocker()
    def test_get_simulation_interfaces(self, mock_requests):
        payload = [{'id': 'foo'}]
        mock_requests.get('http://test/api/v1/simulation-interface/', json=payload)
        res = self.simulation_interface.get_simulation_interfaces()
        self.assertListEqual(res, payload)

    @requests_mock.Mocker()
    def test_get_simulation_interfaces_params(self, mock_requests):
        payload = [{'id': 'foo'}]
        mock_requests.get('http://test/api/v1/simulation-interface/?simulation=abc&original=xyz',
                          json=payload)
        res = self.simulation_interface.get_simulation_interfaces('abc', 'xyz')
        self.assertListEqual(res, payload)
