"""
Tests for worker.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring
from unittest import TestCase
from unittest.mock import MagicMock
import cumulus_air_sdk.air_sdk as sdk

class TestCapacity(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.capacity = sdk.capacity.Capacity(self.api, copies=23)

    def test_init_(self):
        self.assertEqual(self.capacity.capacity_api, self.api)
        self.assertEqual(self.capacity.copies, 23)

class TestCapacityApi(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.api.api_url = 'http://testserver/api'
        self.capacity = sdk.capacity.CapacityApi(self.api)

    def test_init_(self):
        self.assertEqual(self.capacity.api, self.api)
        self.assertEqual(self.capacity.url, 'http://testserver/api/capacity/')

    def test_get_capacity_by_sim(self):
        sim = MagicMock()
        sim.id = '123'
        self.api.get.return_value.json.return_value = {'copies': 1}
        res = self.capacity.get_capacity(sim)
        self.api.get.assert_called_with('http://testserver/api/capacity/123/')
        self.assertEqual(res.copies, 1)

    def test_get_capacity_by_id(self):
        self.api.get.return_value.json.return_value = {'copies': 1}
        res = self.capacity.get_capacity(simulation_id='123')
        self.api.get.assert_called_with('http://testserver/api/capacity/123/')
        self.assertEqual(res.copies, 1)

    def test_get_capacity_missing_param(self):
        with self.assertRaises(ValueError) as err:
            self.capacity.get_capacity()
        self.assertEqual(str(err.exception), 'Must pass a simulation or simulation_id argument')
