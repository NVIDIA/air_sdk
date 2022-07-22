# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for organization.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import organization

class TestOrganization(TestCase):
    def setUp(self):
        self.model = organization.Organization(MagicMock())
        self.model.id = 'abc123'
        self.model.name = 'NVIDIA'

    def test_init_(self):
        self.assertTrue(self.model._deletable)
        self.assertTrue(self.model._updatable)

    def test_repr(self):
        self.assertEqual(str(self.model), f'<Organization {self.model.name} {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))

class TestOrganizationApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = organization.OrganizationApi(self.client)

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/organization/')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get(self, mock_raise):
        self.client.get.return_value.json.return_value = {'test': 'success'}
        res = self.api.get('abc123', foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/organization/abc123/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, organization.Organization)
        self.assertEqual(res.test, 'success')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list(self, mock_raise):
        self.client.get.return_value.json.return_value = [{'id': 'abc'}, {'id': 'xyz'}]
        res = self.api.list(foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/organization/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value, data_type=list)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], organization.Organization)
        self.assertEqual(res[0].id, 'abc')
        self.assertEqual(res[1].id, 'xyz')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create(self, mock_raise):
        self.client.post.return_value.json.return_value = {'id': 'abc'}
        res = self.api.create(name='abc123', members=['def123'])
        self.client.post.assert_called_with(f'{self.client.api_url}/organization/',
                                            json={'name': 'abc123', 'members': ['def123']})
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        self.assertIsInstance(res, organization.Organization)
        self.assertEqual(res.id, 'abc')

    def test_create_required_kwargs(self):
        with self.assertRaises(AttributeError) as err:
            self.api.create(members=[])
        self.assertTrue('requires name' in str(err.exception))
        with self.assertRaises(AttributeError) as err:
            self.api.create(name='abc123')
        self.assertTrue('requires members' in str(err.exception))
