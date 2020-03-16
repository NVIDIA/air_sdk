"""
Tests for simulation.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring

from unittest import TestCase
import requests_mock
from cumulus_air_sdk import AirApi
import cumulus_air_sdk.air_sdk as sdk

class TestSimulation(TestCase):
    def setUp(self):
        self.api = AirApi('http://test/api/', 'v1')
        self.simulation = sdk.Simulation(self.api)

    def test_init(self):
        self.assertEqual(self.simulation.api, self.api)
        self.assertEqual(self.simulation.url, self.api.api_url + '/simulation/')

    @requests_mock.Mocker()
    def test_get_simulations(self, mock_requests):
        sims = [{'id': 'foo'}]
        mock_requests.get(self.simulation.url, json=sims)
        res = self.simulation.get_simulations()
        self.assertListEqual(res, sims)
