# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for account.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring
from unittest import TestCase
from unittest.mock import MagicMock

from ..air_sdk import account

class TestAccount(TestCase):
    def setUp(self):
        self.model = account.Account(MagicMock())
        self.model.username = 'foo'
        self.model.id = 'abc123'
        self.assertFalse(self.model._deletable)
        self.assertFalse(self.model._updatable)

    def test_init(self):
        self.assertFalse(self.model._deletable)
        self.assertFalse(self.model._updatable)

    def test_repr(self):
        self.assertEqual(str(self.model), f'<Account {self.model.username} {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))

class TestAccountApi(TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_client.api_url = 'http://testserver/api'
        self.mock_client.get.return_value.status_code = 200
        self.url = self.mock_client.api_url + '/account/'
        self.api = account.AccountApi(self.mock_client)

    def test_init(self):
        self.assertEqual(self.api.client, self.mock_client)
        self.assertEqual(self.api.url, self.url)

    def test_get(self):
        self.mock_client.get.return_value.json.return_value = {'foo': 'bar'}
        res = self.api.get('abc123', foo='bar')
        self.mock_client.get.assert_called_with(self.url + 'abc123/', params={'foo': 'bar'})
        self.assertIsInstance(res, account.Account)
        self.assertEqual(res.foo, 'bar')

    def test_list(self):
        self.mock_client.get.return_value.json.return_value = [{'foo': 'bar'}]
        res = self.api.list(foo='bar')
        self.mock_client.get.assert_called_with(self.url, params={'foo': 'bar'})
        self.assertEqual(len(res), 1)
        self.assertIsInstance(res[0], account.Account)
        self.assertEqual(res[0].foo, 'bar')
