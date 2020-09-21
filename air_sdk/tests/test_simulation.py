"""
Tests for simulation.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,no-self-use

from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock
import pytest
import requests_mock
from cumulus_air_sdk import AirApi
import cumulus_air_sdk.air_sdk as sdk

class TestSimulation(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.api.api = MagicMock()
        self.data = {'url': 'http://test/api/v1/simulation/abc', 'id': 'abc', 'topology': 'def',
                     'nodes': [{'node1': 'foo'}], 'services': [{'svc1': 'foo'}],
                     'name': 'foo@bar.com', 'expires': True,
                     'expires_at': '2020-03-17T01:00:00.000000Z', 'sleep': True,
                     'sleep_at': '2020-03-15T02:00:00.000000Z', 'netq_username': 'john@doe.com',
                     'netq_password': 'abc123'}
        self.simulation = sdk.simulation.Simulation(self.api, **self.data)

    def test_init(self):
        self.assertEqual(self.simulation.simulation_api, self.api)
        data = deepcopy(self.data)
        data['simulation_api'] = self.api
        self.assertDictEqual(self.simulation.__dict__, data)

    def test_update(self):
        self.api.update_simulation = MagicMock()
        original = deepcopy(self.simulation.__dict__)
        del original['simulation_api']
        new = {'new': 'test'}
        original.update(new)
        self.simulation.update(**new)
        self.api.update_simulation.assert_called_with(self.data['id'], original)

    def test_create_service(self):
        self.api.api.service = MagicMock()
        self.api.api.service.create_service = MagicMock()
        self.simulation.create_service('foo', 'oob-mgmt-server:eth0', 22, foo='bar')
        self.api.api.service.create_service.assert_called_with(self.data['id'], 'foo',
                                                               'oob-mgmt-server:eth0', 22,
                                                               foo='bar')

    def test_add_permission(self):
        self.api.api.permission = MagicMock()
        self.api.api.permission.create_permission = MagicMock()
        self.simulation.add_permission('foo@bar.com', foo='bar')
        self.api.api.permission.create_permission.assert_called_with('foo@bar.com',
                                                                     simulation=self.data['id'],
                                                                     foo='bar')

    def test_start(self):
        self.simulation.start()
        self.api.api.control.assert_called_with(self.simulation.id, 'load')

class TestSimulationApi(TestCase):
    def setUp(self):
        self.api = AirApi('http://test/api/', 'v1')
        self.simulation = sdk.SimulationApi(self.api)

    def test_init(self):
        self.assertEqual(self.simulation.api, self.api)
        self.assertEqual(self.simulation.url, self.api.api_url + '/simulation/')

    @requests_mock.Mocker()
    def test_get_simulations(self, mock_requests):
        sims = [{'id': 'foo'}]
        mock_requests.get(self.simulation.url, json=sims)
        res = self.simulation.get_simulations()
        self.assertListEqual(res, sims)

    def test_update_simulation(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        self.simulation.api.put = MagicMock(return_value=mock_resp)
        payload = {'foo': 'bar'}
        self.simulation.update_simulation('abc', payload)
        self.simulation.api.put.assert_called_with(self.simulation.url + 'abc/', json=payload)

    def test_update_simulation_failed(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        self.simulation.api.put = MagicMock(return_value=mock_resp)
        with pytest.raises(sdk.exceptions.AirUnexpectedResponse) as err:
            self.simulation.update_simulation('abc', {})
            self.assertEqual(err.value, 400)

    @requests_mock.Mocker()
    def test_duplicate(self, mock_requests):
        data = {'simulation': {'id': 'foo'}}
        mock_requests.post(self.simulation.url + 'abc/control/', json=data)
        sim, payload = self.simulation.duplicate('abc')
        self.assertEqual(sim.id, 'foo')
        self.assertEqual(payload, data)

    @requests_mock.Mocker()
    def test_duplicate_bad_code(self, mock_requests):
        mock_requests.post(self.simulation.url + 'abc/control/', status_code=400)
        with pytest.raises(sdk.exceptions.AirUnexpectedResponse) as err:
            self.simulation.duplicate('abc')
            self.assertEqual(err.value, 400)

    @requests_mock.Mocker()
    def test_duplicate_bad_json(self, mock_requests):
        mock_requests.post(self.simulation.url + 'abc/control/', text='foo')
        with pytest.raises(sdk.exceptions.AirUnexpectedResponse) as err:
            self.simulation.duplicate('abc')
            self.assertEqual(err.value, 'foo')

    @requests_mock.Mocker()
    def test_duplicate_no_sim(self, mock_requests):
        mock_requests.post(self.simulation.url + 'abc/control/', json={})
        with pytest.raises(sdk.exceptions.AirUnexpectedResponse) as err:
            self.simulation.duplicate('abc')
            self.assertEqual(err.value, {})

    @requests_mock.Mocker()
    def test_duplicate_kwargs(self, mock_requests):
        data = {'simulation': {'id': 'foo'}}
        mock_requests.post(self.simulation.url + 'abc/control/', json=data)
        self.simulation.duplicate('abc', foo='bar')
        self.assertEqual(mock_requests.call_count, 1)
        self.assertDictEqual(mock_requests.last_request.json(),
                             {'action': 'duplicate', 'foo': 'bar'})

    def test_create_simulation(self):
        api = MagicMock()
        api.api_url = 'http://testserver'
        api.post.return_value.status_code = 201
        api.post.return_value.json.return_value = {'name': 'foo'}
        simulation = sdk.SimulationApi(api)
        sim, json = simulation.create_simulation(foo='bar')
        api.post.assert_called_with('http://testserver/simulation/', json={'foo': 'bar'})
        self.assertEqual(sim.name, 'foo')
        self.assertEqual(json, {'name': 'foo'})

    def test_create_simulation_bad_status(self):
        api = MagicMock()
        api.post.return_value.status_code = 400
        api.post.return_value.data = 'test error'
        simulation = sdk.SimulationApi(api)
        with self.assertRaises(sdk.exceptions.AirUnexpectedResponse) as err:
            simulation.create_simulation(name='foo')
        self.assertEqual(err.exception.message,
                         'Received an unexpected response from the Cumulus AIR API: test error')
        self.assertEqual(err.exception.status_code, 400)

    def test_control(self):
        api = MagicMock()
        api.api_url = 'http://testserver'
        simulation = sdk.SimulationApi(api)
        simulation.control('abc', 'load', foo='bar')
        api.post.assert_called_with('http://testserver/simulation/abc/control/',
                                    json={'action': 'load', 'foo': 'bar'})
