# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for resource_budget.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import resource_budget

class TestResourceBudget(TestCase):
    def setUp(self):
        self.model = resource_budget.ResourceBudget(MagicMock())
        self.model.id = 'abc123'
        self.model.category = 'START'

    def test_init_(self):
        self.assertFalse(self.model._deletable)
        self.assertTrue(self.model._updatable)

    def test_repr(self):
        self.assertEqual(str(self.model), f'<ResourceBudget {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))

class TestResourceBudgetApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = resource_budget.ResourceBudgetApi(self.client)

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/resource-budget/')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get(self, mock_raise):
        self.client.get.return_value.json.return_value = {'test': 'success'}
        res = self.api.get('abc123', foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/resource-budget/abc123/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, resource_budget.ResourceBudget)
        self.assertEqual(res.test, 'success')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list(self, mock_raise):
        self.client.get.return_value.json.return_value = [{'id': 'abc'}, {'id': 'xyz'}]
        res = self.api.list(foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/resource-budget/', params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value, data_type=list)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], resource_budget.ResourceBudget)
        self.assertEqual(res[0].id, 'abc')
        self.assertEqual(res[1].id, 'xyz')
