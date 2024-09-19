# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for fleet.py
"""

# pylint: disable=missing-function-docstring,missing-class-docstring
from unittest import TestCase
from unittest.mock import MagicMock, patch

from air_sdk import fleet, organization


class TestFleet(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.model = fleet.Fleet(self.api)
        self.model.name = 'test.test'
        self.model.id = 'abc123'

    def test_init_(self):
        self.assertTrue(self.model._deletable)
        self.assertTrue(self.model._updatable)

    def test_repr(self):
        self.assertEqual(str(self.model), f'<Fleet {self.model.name} {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))


class TestFleetApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.mock_api = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = fleet.FleetApi(self.client)
        self.org = organization.Organization(self.mock_api, id='xyz456', name='NVIDIA')

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/fleet/')

    @patch('air_sdk.util.raise_if_invalid_response')
    def test_get(self, mock_raise):
        self.client.get.return_value.json.return_value = {'test': 'success'}
        res = self.api.get('abc123', foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/fleet/abc123/', params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, fleet.Fleet)
        self.assertEqual(res.test, 'success')

    @patch('air_sdk.util.raise_if_invalid_response')
    def test_list(self, mock_raise):
        self.client.get.return_value.json.return_value = {
            'count': 2,
            'next': 'blabla',
            'previous': None,
            'results': [{'id': 'abc'}, {'id': 'xyz'}],
        }
        res = self.api.list(foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/fleet/', params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value, data_type=dict)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], fleet.Fleet)
        self.assertEqual(res[0].id, 'abc')
        self.assertEqual(res[1].id, 'xyz')

    @patch('air_sdk.util.raise_if_invalid_response')
    def test_create(self, mock_raise):
        self.client.post.return_value.json.return_value = {'id': 'abc'}
        res = self.api.create(
            name='test_fleet_2', prefix_length=65, organization=str(self.org.id), port_range=22
        )
        self.client.post.assert_called_with(
            f'{self.client.api_url}/fleet/',
            json={
                'name': 'test_fleet_2',
                'prefix_length': 65,
                'organization': str(self.org.id),
                'port_range': 22,
            },
        )
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        self.assertIsInstance(res, fleet.Fleet)
        self.assertEqual(res.id, 'abc')

    def test_create_required_kwargs(self):
        with self.assertRaises(AttributeError) as err:
            self.api.create(prefix_length=65, organization=str(self.org.id), port_range=22)
        self.assertTrue('requires name' in str(err.exception))
        with self.assertRaises(AttributeError) as err:
            self.api.create(name='test_fleet_2', prefix_length=65, port_range=22)
        self.assertTrue('requires organization' in str(err.exception))
