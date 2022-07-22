# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for image.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import image

class TestImage(TestCase):
    def setUp(self):
        self.mock_api = MagicMock()
        self.model = image.Image(self.mock_api)
        self.model.id = 'abc123'
        self.model.name = 'ubuntu'

    def test_init_(self):
        self.assertTrue(self.model._deletable)
        self.assertTrue(self.model._updatable)

    def test_repr(self):
        self.assertEqual(str(self.model), f'<Image {self.model.name} {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))

    @patch('builtins.open')
    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_upload(self, mock_raise, mock_open):
        self.model.upload('myfile')
        mock_put = self.mock_api.client.put
        mock_put.assert_called_with(f'{self.mock_api.url}{self.model.id}/upload/',
                                    data=mock_open.return_value.__enter__.return_value)
        mock_open.assert_called_with('myfile', 'rb')
        mock_raise.assert_called_with(mock_put.return_value, status_code=204, data_type=None)

class TestImageApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = image.ImageApi(self.client)

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/image/')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get(self, mock_raise):
        self.client.get.return_value.json.return_value = {'test': 'success'}
        res = self.api.get('abc123', foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/image/abc123/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, image.Image)
        self.assertEqual(res.test, 'success')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list(self, mock_raise):
        self.client.get.return_value.json.return_value = [{'id': 'abc'}, {'id': 'xyz'}]
        res = self.api.list(foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/image/', params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value, data_type=list)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], image.Image)
        self.assertEqual(res[0].id, 'abc')
        self.assertEqual(res[1].id, 'xyz')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create(self, mock_raise):
        org = 'acb123'
        self.client.post.return_value.json.return_value = {'id': 'abc'}
        res = self.api.create(name='myimage', organization=org)
        self.client.post.assert_called_with(f'{self.client.api_url}/image/',
                                            json={'name': 'myimage', 'organization': org})
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        self.assertIsInstance(res, image.Image)
        self.assertEqual(res.id, 'abc')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    @patch('air_sdk.air_sdk.image.Image.upload')
    def test_create_upload(self, mock_upload, mock_raise):
        org = 'abc123'
        self.client.post.return_value.json.return_value = {'id': 'abc'}
        res = self.api.create(name='myimage', filename='myfile', organization=org)
        self.client.post.assert_called_with(f'{self.client.api_url}/image/',
                                            json={'name': 'myimage', 'filename': 'myfile',
                                                  'organization': org})
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        mock_upload.assert_called_with('myfile')
        self.assertIsInstance(res, image.Image)

    def test_create_required_kwargs(self):
        with self.assertRaises(AttributeError) as err:
            self.api.create(organization='abc123')
        self.assertTrue('requires name' in str(err.exception))
        with self.assertRaises(AttributeError) as err:
            self.api.create(name='abc123')
        self.assertTrue('requires organization' in str(err.exception))
