# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for token.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import token

class TestAPIToken(TestCase):
    def setUp(self):
        self.model = token.Token(MagicMock())
        # self.model.id = 'abc123'
        # self.model.token = 'abc123'
        self.model.name = 'public'

    def test_init_(self):
        self.assertTrue(self.model._deletable)
        self.assertFalse(self.model._updatable)

    def test_repr(self):
        self.assertEqual(str(self.model), f'<Token {self.model.name}>')

    def test_repr_id(self):
        self.model.id = 'abc123'
        self.assertEqual(str(self.model), f'<Token {self.model.name} {self.model.id}>')

    def test_repr_token(self):
        self.model.token = 'abc123'
        self.assertEqual(str(self.model), f'<Token {self.model.name} {self.model.token}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))


class TestTokenApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = token.TokenApi(self.client)

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/api-token/')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list(self, mock_raise):
        self.client.get.return_value.json.return_value = [{'id': 'abc'}, {'id': 'xyz'}]
        res = self.api.list(foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/api-token/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value, data_type=list)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], token.Token)
        self.assertEqual(res[0].id, 'abc')
        self.assertEqual(res[1].id, 'xyz')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create(self, mock_raise):
        self.client.post.return_value.json.return_value = {'id': 'abc'}
        res = self.api.create(name='test')
        self.client.post.assert_called_with(f'{self.client.api_url}/api-token/',
                                            json={'name': 'test'})
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        self.assertIsInstance(res, token.Token)
        self.assertEqual(res.id, 'abc')

    def test_create_required_kwargs(self):
        with self.assertRaises(AttributeError) as err:
            self.api.create()
        self.assertTrue('requires name' in str(err.exception))

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_delete(self, mock_raise):
        self.api.delete('abc')
        self.client.delete.assert_called_with(f'{self.client.api_url}/api-token/abc/',
                                              params={})
        mock_raise.assert_called_with(self.client.delete.return_value, status_code=204,
                                      data_type=None)
