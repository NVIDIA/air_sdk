"""
Tests for simulation.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,duplicate-code
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import simulation

class TestSimulation(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.api.url = 'http://testserver/api/'
        self.model = simulation.Simulation(self.api)
        self.model.id = 'abc123'
        self.model.title = 'test'

    def test_init_(self):
        self.assertFalse(self.model._deletable)
        self.assertTrue(self.model._updatable)
        self.assertEqual(self.model.services, [])

    def test_repr(self):
        self.assertEqual(str(self.model), f'<Simulation \'{self.model.title}\' {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))


    def test_create_service(self):
        res = self.model.create_service('test', 'intf', 22, foo='bar')
        self.api.client.services.create.assert_called_with(simulation=self.model.id, name='test',
                                                           interface='intf', dest_port=22,
                                                           foo='bar')
        self.assertEqual(self.model.services, [res])
        self.assertEqual(res, self.api.client.services.create.return_value)

    def test_add_permission(self):
        res = self.model.add_permission('me@test.com', foo='bar')
        self.api.client.permissions.create.assert_called_with(email='me@test.com',
                                                              simulation=self.model.id, foo='bar')
        self.assertEqual(res, self.api.client.permissions.create.return_value)

    @patch('cumulus_air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_control(self, mock_raise):
        res = self.model.control(action='test')
        self.api.client.post(f'{self.api.url}{self.model.id}/control/', json={'action': 'test'})
        mock_raise.assert_called_with(self.api.client.post.return_value)
        self.assertEqual(res, self.api.client.post.return_value.json.return_value)

    def test_control_required_kwargs(self):
        with self.assertRaises(AttributeError) as err:
            self.model.control()
        self.assertTrue('requires action' in str(err.exception))

    @patch('cumulus_air_sdk.air_sdk.simulation.Simulation.control')
    def test_start(self, mock_control):
        self.model.start()
        mock_control.assert_called_with(action='load')

    @patch('cumulus_air_sdk.air_sdk.simulation.Simulation.control')
    def test_store(self, mock_control):
        self.model.store()
        mock_control.assert_called_with(action='store')

    @patch('cumulus_air_sdk.air_sdk.simulation.Simulation.control')
    def test_delete(self, mock_control):
        self.model.delete()
        mock_control.assert_called_with(action='destroy')

class TestSimulationApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = simulation.SimulationApi(self.client)

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/simulation/')

    @patch('cumulus_air_sdk.air_sdk.simulation.SimulationApi.list')
    def test_get_simulations(self, mock_list):
        self.assertEqual(self.api.get_simulations(), mock_list.return_value)

    @patch('cumulus_air_sdk.air_sdk.simulation.SimulationApi.get')
    def test_get_simulation(self, mock_get):
        res = self.api.get_simulation('abc123')
        mock_get.assert_called_with('abc123')
        self.assertEqual(res, mock_get.return_value)

    @patch('cumulus_air_sdk.air_sdk.simulation.SimulationApi.create')
    def test_create_simulation(self, mock_create):
        res = self.api.create_simulation(foo='bar')
        mock_create.assert_called_with(foo='bar')
        self.assertEqual(res, mock_create.return_value)

    @patch('cumulus_air_sdk.air_sdk.simulation.SimulationApi.get')
    def test_update_simulation(self, mock_get):
        self.api.update_simulation('abc123', {'foo': 'bar'})
        mock_get.assert_called_with('abc123')
        mock_get.return_value.update.assert_called_with(foo='bar')

    @patch('cumulus_air_sdk.air_sdk.simulation.SimulationApi.get')
    @patch('cumulus_air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_duplicate(self, mock_raise, mock_get):
        mock_get.return_value.control.return_value.json.return_value = {'simulation':
                                                                        {'test': 'xyz'}}
        sim, res = self.api.duplicate('abc123', foo='bar')
        mock_get.assert_called_with('abc123')
        mock_get.return_value.control.assert_called_with(foo='bar', action='duplicate')
        mock_raise.assert_called_with(mock_get.return_value.control.return_value)
        self.assertIsInstance(sim, simulation.Simulation)
        self.assertEqual(sim.test, 'xyz')
        self.assertEqual(res, mock_get.return_value.control.return_value.json.return_value)

    @patch('cumulus_air_sdk.air_sdk.simulation.SimulationApi.get')
    def test_control(self, mock_get):
        res = self.api.control('abc123', 'test', foo='bar')
        mock_get.assert_called_with('abc123')
        mock_get.return_value.control.assert_called_with(action='test', foo='bar')
        self.assertEqual(res, mock_get.return_value.control.return_value)

    @patch('cumulus_air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get_citc_simulation(self, mock_raise):
        self.client.get.return_value.json.return_value = {'foo': 'bar'}
        res = self.api.get_citc_simulation()
        self.client.get.assert_called_with(f'{self.client.api_url}/simulation/citc/')
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, simulation.Simulation)
        self.assertEqual(res.foo, 'bar')

    @patch('cumulus_air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get(self, mock_raise):
        self.client.get.return_value.json.return_value = {'test': 'success'}
        res = self.api.get('abc123', foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/simulation/abc123/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, simulation.Simulation)
        self.assertEqual(res.test, 'success')

    @patch('cumulus_air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list(self, mock_raise):
        self.client.get.return_value.json.return_value = [{'id': 'abc'}, {'id': 'xyz'}]
        res = self.api.list(foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/simulation/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value, data_type=list)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], simulation.Simulation)
        self.assertEqual(res[0].id, 'abc')
        self.assertEqual(res[1].id, 'xyz')

    @patch('cumulus_air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create(self, mock_raise):
        self.client.post.return_value.json.return_value = {'id': 'abc'}
        res = self.api.create(topology='abc123')
        self.client.post.assert_called_with(f'{self.client.api_url}/simulation/',
                                            json={'topology': 'abc123'})
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        self.assertIsInstance(res, simulation.Simulation)
        self.assertEqual(res.id, 'abc')

    def test_create_required_kwargs(self):
        with self.assertRaises(AttributeError) as err:
            self.api.create()
        self.assertTrue('requires topology' in str(err.exception))
