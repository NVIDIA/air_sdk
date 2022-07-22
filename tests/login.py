# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for login.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import login

class TestLogin(TestCase):
    def setUp(self):
        self.model = login.Login(MagicMock())
        self.model.id = 'abc123'

    def test_init_(self):
        self.assertFalse(self.model._deletable)
        self.assertFalse(self.model._updatable)

    def test_repr(self):
        self.assertEqual(str(self.model), f'<Login {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))

class TestLoginApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = login.LoginApi(self.client)

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/login/')

    @patch('air_sdk.air_sdk.login.LoginApi.list')
    def test_get(self, mock_list):
        res = self.api.get(foo='bar')
        mock_list.assert_called_with(foo='bar')
        self.assertEqual(res, mock_list.return_value)

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list(self, mock_raise):
        self.client.get.return_value.json.return_value = {'id': 'abc'}
        res = self.api.list(foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/login/', params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, login.Login)
        self.assertEqual(res.id, 'abc')
