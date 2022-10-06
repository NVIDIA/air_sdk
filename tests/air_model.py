# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for air_model.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,unused-argument
#pylint: disable=too-many-public-methods,duplicate-code,protected-access
import datetime as dt
from datetime import date, datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import air_model
from ..air_sdk.exceptions import AirObjectDeleted
from ..air_sdk.node import Node

@patch('air_sdk.air_sdk.util.raise_if_invalid_response')
class TestAirModel(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.model = air_model.AirModel(self.api, foo='bar')
        self.model._api.client.patch = MagicMock()
        self.model._api.client.put = MagicMock()
        self.model._api.client.delete = MagicMock()
        self.model.id = 'abc123'

    def test_init(self, mock_raise):
        self.assertFalse(self.model._deleted)
        self.assertTrue(self.model._updatable)
        self.assertTrue(self.model._deletable)
        self.assertEqual(self.model._api, self.api)
        self.assertEqual(self.model.foo, 'bar')

    def test_model_keys(self, mock_raise):
        model_keys = {'account': 'accounts', 'base_simulation': 'simulations', 'bios': 'images',
                      'connection': 'links', 'demo': 'demos', 'interface': 'simulation_interfaces',
                      'interfaces': {'Node': 'interfaces',
                                     'SimulationNode': 'simulation_interfaces',
                                     'Link': 'interfaces'},
                      'job': 'jobs', 'last_worker': 'worker',
                      'node': {'Interface': 'nodes', 'NodeInstruction': 'simulation_nodes',
                               'SimulationInterface': 'simulation_nodes',
                               'TopologyInstruction': 'nodes'},
                      'nodes': 'simulation_nodes',
                      'original': {'SimulationInterface': 'interfaces',
                                   'SimulationNode': 'nodes'},
                      'organization': 'organizations', 'os': 'images',
                      'preferred_worker': 'workers', 'services': 'services',
                      'simulation': 'simulations', 'topology': 'topologies', 'worker': 'workers'}
        self.assertDictEqual(self.model.model_keys, model_keys)

    def test_load(self, mock_raise):
        model = air_model.AirModel(self.api, normal='http://testserver/api/v1/thing3/abc456')
        self.assertEqual(model.normal, 'http://testserver/api/v1/thing3/abc456')

    def test_load_datetime(self, mock_raise):
        model = air_model.AirModel(self.api, expires_at='2030-12-12T22:05:03')
        self.assertIsInstance(model.expires_at, (datetime, date))

    @patch('air_sdk.air_sdk.air_model.AirModel.model_keys', {'lazy_list': 'lazy_api'})
    @patch('air_sdk.air_sdk.air_model.LazyLoadedList.__getitem__')
    def test_load_list(self, mock_list_get, mock_raise):
        model = air_model.AirModel(self.api, lazy_list=['http://testserver/api/v1/thing/abc123'])
        self.assertIsInstance(model.lazy_list, air_model.LazyLoadedList)
        self.assertEqual(model.lazy_list[0].id, mock_list_get.return_value.id)

    @patch('air_sdk.air_sdk.air_model.AirModel.model_keys', {'lazy_lazy': 'lazy_api'})
    def test_load_lazy_exists(self, mock_raise):
        lazy = air_model.LazyLoaded('def123', 'lazy')
        model = air_model.AirModel(self.api, lazy_lazy=lazy)
        self.assertEqual(model.lazy_lazy, self.api.client.lazy.get.return_value)

    @patch('air_sdk.air_sdk.air_model.AirModel.model_keys', {'lazy_item': 'lazy_api'})
    def test_load_http(self, mock_raise):
        model = air_model.AirModel(self.api, lazy_item='http://testserver/api/v1/thing2/xyz123')
        self.assertEqual(model.lazy_item.id, self.api.client.lazy_api.get.return_value.id)

    @patch('air_sdk.air_sdk.air_model.AirModel.model_keys', {'lazy_item': 'lazy_api'})
    def test_load_lazy(self, mock_raise):
        model = air_model.AirModel(self.api, lazy_item='xyz123')
        self.assertEqual(model.lazy_item.id, self.api.client.lazy_api.get.return_value.id)

    def test_repr(self, mock_raise):
        self.assertRegex(str(self.model),
                         r'<air_sdk.air_sdk.air_model.AirModel object at 0x[0-9a-f]+>')

    def test_repr_deleted(self, mock_raise):
        self.model._deleted = True
        self.assertRegex(str(self.model),
                         r'<Deleted Object \(<air_sdk.air_sdk.air_model.AirModel ' +
                         r'object at 0x[0-9a-f]+>\)>')

    def test_getattribute_get_deleted(self, mock_raise):
        self.assertFalse(self.model._deleted)
        self.api.client.get.assert_not_called()

    def test_getattribute_deleted(self, mock_raise):
        self.model._deleted = True
        with self.assertRaises(AirObjectDeleted) as err:
            _ = self.model.foo
        self.assertEqual(err.exception.message,
                         '<class \'air_sdk.air_sdk.air_model.AirModel\'> object has ' + \
                         'been deleted and should no longer be referenced')

    def test_getattribute_lazy(self, mock_raise):
        self.model.lazy = air_model.LazyLoaded('abc123', 'thing')
        self.assertEqual(self.model.lazy, self.api.client.thing.get.return_value)
        self.api.client.thing.get.assert_called_with('abc123')

    def test_setattr_set_deleted(self, mock_raise):
        self.model._deleted = True
        self.assertTrue(self.model._deleted)

    @patch('air_sdk.air_sdk.air_model.AirModel._patch')
    def test_setattr_not_updatable(self, mock_patch, mock_raise):
        self.model._updatable = False
        mock_patch.reset_mock()
        self.model.foo = 'test'
        self.assertEqual(self.model.foo, 'test')
        mock_patch.assert_not_called()

    def test_setattr(self, mock_raise):
        self.model._patch = MagicMock()
        self.model.foo = 'test'
        self.model._patch.assert_called_with('foo', 'test')
        self.assertEqual(self.model.foo, 'test')

    def test_setattr_no_change(self, mock_raise):
        self.model._patch = MagicMock()
        self.model.foo = 'bar'
        self.model._patch.assert_not_called()
        self.assertEqual(self.model.foo, 'bar')

    def test_setattr_internal(self, mock_raise):
        self.model._patch = MagicMock()
        self.model._foo = 'bar'
        self.model._patch.assert_not_called()
        self.assertEqual(self.model._foo, 'bar')

    @patch('air_sdk.air_sdk.air_model.AirModel.model_keys', {'simulation': 'simulations'})
    def test_get_model_key(self, mock_raise):
        self.assertEqual(self.model._get_model_key('simulation'), 'simulations')

    @patch('air_sdk.air_sdk.air_model.AirModel.model_keys',
           {'simulation': {'Node': 'a', 'Node2': 'b'}})
    def test_get_model_key_dict(self, mock_raise):
        node = Node(MagicMock())
        self.assertEqual(node._get_model_key('simulation'), 'a')

    def test_patch(self, mock_raise):
        self.model.id = 'abc123'
        self.model._patch('foo', 'bar')
        self.model._api.client.patch.assert_called_with(f'{self.api.url}abc123/',
                                                        json={'foo': 'bar'})
        mock_raise.assert_called_with(self.model._api.client.patch.return_value)

    @patch('air_sdk.air_sdk.air_model.AirModel.refresh')
    def test_update(self, mock_refresh, mock_raise):
        self.model.update(test='new')
        mock_refresh.assert_called()
        self.model._api.client.put.assert_called_with(f'{self.model._api.url}{self.model.id}/',
                                                      json=self.model.__dict__)
        mock_raise.assert_called_with(self.model._api.client.put.return_value)
        self.assertEqual(self.model.test, 'new')

    def test_update_not_updatable(self, mock_raise):
        self.model._updatable = False
        with self.assertRaises(NotImplementedError) as err:
            self.model.update(test='new')
        self.assertEqual(str(err.exception), 'AirModel does not support updates')

    def test_update_ignored_fields(self, mock_raise):
        self.model.ignore_me = True
        self.model._ignored_update_fields = ['ignore_me']
        self.model.update(test='new')
        payload = self.model.__dict__
        del payload['ignore_me']
        self.model._api.client.put.assert_called_with(f'{self.model._api.url}{self.model.id}/',
                                                      json=payload)
        mock_raise.assert_called_with(self.model._api.client.put.return_value)
        self.assertEqual(self.model.test, 'new')

    def test_delete(self, mock_raise):
        self.model.delete()
        self.assertTrue(self.model._deleted)
        self.model._deleted = False
        self.model._api.client.delete.assert_called_with(f'{self.model._api.url}{self.model.id}/')
        mock_raise.assert_called_with(self.model._api.client.delete.return_value, data_type=None,
                                      status_code=204)

    def test_delete_not_deletable(self, mock_raise):
        self.model._deletable = False
        with self.assertRaises(NotImplementedError) as err:
            self.model.delete()
        self.assertEqual(str(err.exception), 'AirModel does not support deletes')

    @patch('air_sdk.air_sdk.AirModel._load')
    def test_refresh(self, mock_load, mock_raise):
        self.model.refresh()
        self.model._api.get.assert_called_with(self.model.id)
        mock_load.assert_called_with(**self.model._api.get.return_value.__dict__)

    def test_json(self, mock_raise):
        self.assertEqual(self.model.json(), '{"foo": "bar", "id": "abc123"}')

    def test_json_private(self, mock_raise):
        self.model._private = 'foo'
        self.assertEqual(self.model.json(), '{"foo": "bar", "id": "abc123"}')

    def test_json_lazy_loaded(self, mock_raise):
        self.model.test = air_model.LazyLoaded('foo', 'bar')
        self.assertEqual(self.model.json(), '{"foo": "bar", "id": "abc123", "test": "foo"}')

    def test_json_lazy_loaded_list(self, mock_raise):
        self.model.test = air_model.LazyLoadedList([air_model.LazyLoaded('a', 1),
                                                    air_model.LazyLoaded('b', 2)], MagicMock())
        self.assertEqual(self.model.json(), '{"foo": "bar", "id": "abc123", "test": ["a", "b"]}')

    def test_json_datetime(self, mock_raise):
        time = dt.datetime(2030, 12, 12, 22, 5, 3)
        self.model.test = time
        self.assertEqual(self.model.json(),
                         '{"foo": "bar", "id": "abc123", "test": "2030-12-12T22:05:03"}')

class TestLazyLoaded(TestCase):
    def setUp(self):
        self.model = air_model.LazyLoaded('abc123', 'tests')

    def test_init(self):
        self.assertEqual(self.model.id, 'abc123')
        self.assertEqual(self.model.model, 'tests')

    def test_repr(self):
        self.assertEqual(str(self.model), f'<air_sdk.air_model.LazyLoaded Test {self.model.id}>')

    def test_repr_topology(self):
        model = air_model.LazyLoaded('abc123', 'topologies')
        self.assertEqual(str(model), f'<air_sdk.air_model.LazyLoaded Topology {self.model.id}>')

class TestLazyLoadedList(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.item1 = air_model.LazyLoaded('abc', 'tests')
        self.item2 = air_model.LazyLoaded('xyz', 'tests')
        self.model = air_model.LazyLoadedList([self.item1, self.item2], self.api)

    def test_init(self):
        self.assertEqual(self.model._api, self.api)
        self.assertListEqual(self.model, [self.item1, self.item2])

    def test_getitem(self):
        self.assertEqual(self.model[0], self.api.client.tests.get.return_value)
        self.api.client.tests.get.assert_called_with('abc')

    def test_iter(self):
        mock_item = MagicMock()
        mock_item.test = 'foo'
        self.api.client.tests.get.return_value = mock_item
        for item in self.model:
            self.assertEqual(item.test, 'foo')

class TestHelpers(TestCase):
    def test_get_item_id(self):
        self.assertEqual(air_model._get_item_id('foo'), 'foo')

    def test_get_item_id_dict(self):
        self.assertEqual(air_model._get_item_id({'id': 'abc123'}), 'abc123')

    def test_get_item_id_url(self):
        self.assertEqual(air_model._get_item_id('http://testserver/api/v1/test/abc123'), 'abc123')
