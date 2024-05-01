# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for userconfig.py
"""

from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import organization, userconfig, util


class TestUserConfig(TestCase):
    def setUp(self):
        self.api = MagicMock()
        self.model = userconfig.UserConfig(
            self.api,
            id='uuid',
            name='my-script',
            kind=userconfig.UserConfig.KIND_CLOUD_INIT_USER_DATA,
            content='abc123',
            organization='uuid',
        )

    def test_init(self):
        self.assertTrue(self.model._deletable)
        self.assertTrue(self.model._updatable)
        self.assertEqual(self.model.KIND_CLOUD_INIT_USER_DATA, 'cloud-init-user-data')
        self.assertEqual(self.model.KIND_CLOUD_INIT_META_DATA, 'cloud-init-meta-data')

    def test_repr(self):
        self.assertEqual(str(self.model), f'<UserConfig {self.model.name} {self.model.kind} {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in repr(self.model))


class TestUserConfigAPI(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api'
        self.api = userconfig.UserConfigAPI(self.client)

        self.script_name = 'my-script'
        self.script_kind = self.api.model.KIND_CLOUD_INIT_USER_DATA
        self.organization = organization.Organization(self.client, id='org-id', name='my-org')

    def test_init(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.API_VERSION, 2)
        self.assertEqual(self.api.API_PATH, 'userconfigs')
        self.assertEqual(self.api.url, f'http://testserver/api/{self.api.API_PATH}/')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create_from_plaintext(self, _: MagicMock):
        content = 'blabla'
        self.api.create(
            name=self.script_name, kind=self.script_kind, organization=self.organization, content=content
        )
        self.client.post.assert_called_with(
            util.url_path_join(self.api.parsed_url, trailing_slash=True).geturl(),
            json={
                'name': self.script_name,
                'kind': self.script_kind,
                'organization': self.organization,
                'content': content,
            },
        )

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create_from_path_string(self, _: MagicMock):
        content = 'blabla'
        with NamedTemporaryFile('w+', delete=True) as content_file:
            content_file.write(content)
            content_file.flush()

            self.api.create(
                name=self.script_name,
                kind=self.script_kind,
                organization=self.organization,
                content=content_file.name,
            )
            self.client.post.assert_called_with(
                util.url_path_join(self.api.parsed_url, trailing_slash=True).geturl(),
                json={
                    'name': self.script_name,
                    'kind': self.script_kind,
                    'organization': self.organization,
                    'content': content,
                },
            )

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create_from_path(self, _: MagicMock):
        content = 'blabla'
        with NamedTemporaryFile('w+', delete=True) as content_file:
            content_file.write(content)
            content_file.flush()

            self.api.create(
                name=self.script_name,
                kind=self.script_kind,
                organization=self.organization,
                content=Path(content_file.name),
            )
            self.client.post.assert_called_with(
                util.url_path_join(self.api.parsed_url, trailing_slash=True).geturl(),
                json={
                    'name': self.script_name,
                    'kind': self.script_kind,
                    'organization': self.organization,
                    'content': content,
                },
            )

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create_from_open_file(self, _: MagicMock):
        content = 'blabla'
        with NamedTemporaryFile('w+', delete=True) as content_file:
            content_file.write(content)
            content_file.flush()
            content_file.seek(0)

            self.api.create(
                name=self.script_name,
                kind=self.script_kind,
                organization=self.organization,
                content=content_file.file,
            )
            self.client.post.assert_called_with(
                util.url_path_join(self.api.parsed_url, trailing_slash=True).geturl(),
                json={
                    'name': self.script_name,
                    'kind': self.script_kind,
                    'organization': self.organization,
                    'content': content,
                },
            )

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create_from_path_not_found(self, _: MagicMock):
        with NamedTemporaryFile('r', delete=True) as content_file:
            file_path = Path(content_file.name)

        with self.assertRaises(FileNotFoundError):
            self.api.create(
                name=self.script_name,
                kind=self.script_kind,
                organization=self.organization,
                content=file_path,
            )

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_create_bad_content_argument(self, _: MagicMock):
        with NamedTemporaryFile('wb', delete=True) as content_file:
            content_file.write(b'abcd')
            content_file.flush()
            content_file.seek(0)

            with self.assertRaises(AttributeError):
                self.api.create(
                    name=self.script_name,
                    kind=self.script_kind,
                    organization=self.organization,
                    content=content_file.file,
                )
