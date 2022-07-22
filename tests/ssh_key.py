# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for ssh_key.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import ssh_key

class TestSSHKey(TestCase):
    def setUp(self):
        self.model = ssh_key.SSHKey(MagicMock())
        self.model.id = 'abc123'
        self.model.name = 'public'

    def test_init_(self):
        self.assertTrue(self.model._deletable)
        self.assertFalse(self.model._updatable)

    def test_repr(self):
        self.assertEqual(str(self.model), f'<SSHKey {self.model.name} {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))


class TestSSHKeyApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = ssh_key.SSHKeyApi(self.client)

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/sshkey/')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list(self, mock_raise):
        self.client.get.return_value.json.return_value = [{'id': 'abc'}, {'id': 'xyz'}]
        res = self.api.list(foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/sshkey/', params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value, data_type=list)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], ssh_key.SSHKey)
        self.assertEqual(res[0].id, 'abc')
        self.assertEqual(res[1].id, 'xyz')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create(self, mock_raise):
        self.client.post.return_value.json.return_value = {'id': 'abc'}
        res = self.api.create(public_key='abc123', name='test')
        self.client.post.assert_called_with(f'{self.client.api_url}/sshkey/',
                                            json={'public_key': 'abc123', 'name': 'test'})
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        self.assertIsInstance(res, ssh_key.SSHKey)
        self.assertEqual(res.id, 'abc')

    def test_create_required_kwargs(self):
        with self.assertRaises(AttributeError) as err:
            self.api.create(name='test')
        self.assertTrue('requires public_key' in str(err.exception))
        with self.assertRaises(AttributeError) as err:
            self.api.create(public_key='abc123')
        self.assertTrue('requires name' in str(err.exception))
