# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for topology_file.py
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import topology_file


class TestTopologyFile(TestCase):
    def setUp(self):
        self.model = topology_file.TopologyFile(MagicMock())
        self.model.id = 'abc123'

    def test_repr(self):
        self.assertEqual(str(self.model), f'<TopologyFile {self.model.id}>')


class TestTopologyFileApi(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.api_url = 'http://testserver/api/v1'
        self.api = topology_file.TopologyFileApi(self.client)

    def test_init(self):
        self.assertEqual(self.api.client, self.client)
        self.assertEqual(self.api.url, 'http://testserver/api/v2/topology-file/')

    @patch('air_sdk.air_sdk.util.raise_if_invalid_response')
    def test_get(self, mock_raise):
        file_id = 'abc123'
        kwargs = {'foo': 'bar'}
        self.client.get.return_value.json.return_value = {'test': 'success'}

        res = self.api.get(file_id, **kwargs)
        self.client.get.assert_called_with(f'{self.api.url}{file_id}/', params=kwargs)
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, topology_file.TopologyFile)
