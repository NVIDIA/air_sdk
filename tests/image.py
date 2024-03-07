# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for image.py
"""
import uuid
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk.exceptions import AirUnexpectedResponse
from ..air_sdk.image import Image, ImageApi
from ..air_sdk.organization import Organization


class TestImage(TestCase):
    def setUp(self):
        self.mock_api = MagicMock()
        self.model = Image(self.mock_api)
        self.model.id = 'abc123'
        self.model.name = 'ubuntu'
        self.org1 = Organization(self.mock_api, id='xyz456', name='NVIDIA')

    def test_init_(self):
        self.assertTrue(self.model._deletable)
        self.assertTrue(self.model._updatable)

    def test_repr(self):
        self.assertEqual(str(self.model), f'<Image {self.model.name} {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_copy(self, mock_raise):
        new_id = 'def456'
        mock_post = self.mock_api.client.post
        mock_post.return_value.json.return_value = {'id': new_id, 'name': 'new-image'}
        res = self.model.copy(self.org1)
        mock_post.assert_called_once_with(
            f'{self.mock_api.url}{self.model.id}/copy/', json={'organization': self.org1}
        )
        mock_raise.assert_called_once_with(self.mock_api.client.post.return_value, status_code=201)
        self.assertEqual(res.id, new_id)

    @patch('builtins.open')
    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_upload(self, mock_raise, mock_open):
        self.model.upload('myfile')
        mock_put = self.mock_api.client.put
        mock_put.assert_called_with(
            f'{self.mock_api.url}{self.model.id}/upload/', data=mock_open.return_value.__enter__.return_value
        )
        mock_open.assert_called_with('myfile', 'rb')
        mock_raise.assert_called_with(mock_put.return_value, status_code=204, data_type=None)

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_publish(self, mock_raise):
        self.model.publish(contact='contact@nvidia.com')
        mock_put = self.mock_api.client.put
        mock_put.assert_called_with(
            f'{self.mock_api.url}{self.model.id}/publish/', json={'contact': 'contact@nvidia.com'}
        )
        mock_raise.assert_called_with(mock_put.return_value, status_code=204, data_type=None)

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_unpublish(self, mock_raise):
        self.model.unpublish()
        mock_delete = self.mock_api.client.delete
        mock_delete.assert_called_with(f'{self.mock_api.url}{self.model.id}/publish/')
        mock_raise.assert_called_with(mock_delete.return_value, status_code=204, data_type=None)


class TestImageApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.image_post_url = f'{self.client.api_url}/image/'
        self.api = ImageApi(self.client)

    @staticmethod
    def get_test_image_create_info(**kwargs):
        """Get all required kwargs for creating an image.

        This represents the base amount of information needed to create an image.
        Additional `kwargs` passed will overwrite these default values.
        """
        return {
            'name': 'myimage',
            'organization': 'acb123',
            'version': '3.7.11',
            'default_username': 'cumulus',
            'default_password': 'cumulus!',
            'cpu_arch': 'x86',
            **kwargs,
        }

    def test_init_(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, self.image_post_url)
        self.assertEqual(self.api.url, 'http://testserver/api/image/')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get(self, mock_raise):
        image_id = str(uuid.uuid4())
        self.client.get.return_value.json.return_value = {'test': 'success'}
        res = self.api.get(image_id, foo='bar')
        self.client.get.assert_called_with(f'{self.image_post_url}{image_id}/', params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, Image)
        self.assertEqual(res.test, 'success')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_list(self, mock_raise):
        first_image_id = str(uuid.uuid4())
        second_image_id = str(uuid.uuid4())
        self.client.get.return_value.json.return_value = [{'id': first_image_id}, {'id': second_image_id}]
        res = self.api.list(foo='bar')
        self.client.get.assert_called_with(self.image_post_url, params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value, data_type=list)
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0], Image)
        self.assertEqual(res[0].id, first_image_id)
        self.assertEqual(res[1].id, second_image_id)

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create(self, mock_raise):
        image_id = str(uuid.uuid4())
        self.client.post.return_value.json.return_value = {'id': image_id}
        payload = self.get_test_image_create_info()
        image = self.api.create(**payload)
        self.client.post.assert_called_with(self.image_post_url, json=payload)
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        self.assertIsInstance(image, Image)
        self.assertEqual(image.id, image_id)

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    @patch('air_sdk.air_sdk.image.Image.upload')
    @patch('air_sdk.air_sdk.image.Image.refresh')
    def test_create_upload(self, mock_refresh, mock_upload, mock_raise):
        image_id = str(uuid.uuid4())
        self.client.post.return_value.json.return_value = {'id': image_id}
        payload = self.get_test_image_create_info(filename='myfile')
        image = self.api.create(**payload)
        self.client.post.assert_called_with(self.image_post_url, json=payload)
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        mock_upload.assert_called_with(payload['filename'])
        mock_refresh.assert_called_with()
        self.assertIsInstance(image, Image)

    def test_create_required_kwargs(self):
        with self.assertRaises(AttributeError) as err:
            self.api.create(organization='abc123')
        self.assertTrue('requires name' in str(err.exception))
        with self.assertRaises(AttributeError) as err:
            self.api.create(name='abc123')
        self.assertTrue('requires organization' in str(err.exception))

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    @patch('air_sdk.air_sdk.image.Image.upload', side_effect=AirUnexpectedResponse)
    @patch('air_sdk.air_sdk.image.Image.refresh')
    def test_create_with_upload_failure(self, mock_refresh, mock_upload, mock_raise):
        """Ensure that upload failures are caught and that the image is still returned."""
        self.client.post.return_value.json.return_value = {'id': str(uuid.uuid4())}
        payload = self.get_test_image_create_info(filename='myfile')
        image = self.api.create(**payload)
        self.client.post.assert_called_with(self.image_post_url, json=payload)
        mock_raise.assert_called_with(self.client.post.return_value, status_code=201)
        mock_upload.assert_called_with(payload['filename'])
        mock_refresh.assert_called_with()
        assert isinstance(image, Image)
