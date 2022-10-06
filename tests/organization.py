# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for organization.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,protected-access
from copy import deepcopy
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import organization

class TestOrganization(TestCase):
    def setUp(self):
        self.api = MagicMock()
        mock_res = MagicMock()
        self.api.client.post.return_value = mock_res
        self.model = organization.Organization(self.api, id='abc123', name='NVIDIA')
        self.model._api_url = '/organization/'

    def test_init(self):
        self.assertTrue(self.model._deletable)
        self.assertTrue(self.model._updatable)
        self.assertEqual(self.model.ORG_MEMBER_ROLE, 'Organization Member')
        self.assertEqual(self.model._members_api_url,
                         f'{self.api.url}{self.model.id}/members/')

    def test_repr(self):
        self.assertEqual(str(self.model), f'<Organization {self.model.name} {self.model.id}>')

    def test_repr_deleted(self):
        self.model._deleted = True
        self.assertTrue('Deleted Object' in str(self.model))

    @patch('air_sdk.air_sdk.organization.Organization.refresh')
    def test_add_member(self, mock_refresh):
        username = 'user1@nvidia.com'
        self.model.add_member(username)
        self.api.client.post.assert_called_once_with(self.model._members_api_url,
                                                     json={'username': username,
                                                           'roles': [self.model.ORG_MEMBER_ROLE]})
        mock_refresh.assert_called_once()

    @patch('air_sdk.air_sdk.organization.Organization.refresh')
    def test_add_member_with_role(self, mock_refresh):
        username = 'user1@nvidia.com'
        role = 'test role'
        self.model.add_member(username, [role])
        self.api.client.post.assert_called_once_with(self.model._members_api_url,
                                                     json={'username': username, 'roles': [role]})
        mock_refresh.assert_called_once()

    @patch('air_sdk.air_sdk.organization.Organization.refresh')
    def test_add_members(self, mock_refresh):
        member1 = {'username': 'user1@nvidia.com', 'roles': ['Organization Admin']}
        member2 = {'username': 'user2@nvidia.com'}
        member2_with_role = deepcopy(member2)
        member2_with_role['roles'] = [self.model.ORG_MEMBER_ROLE]
        self.model.add_members([member1, member2])
        self.api.client.post.assert_called_once_with(self.model._members_api_url,
                                                     json=[member1, member2_with_role])
        mock_refresh.assert_called_once()

    @patch('air_sdk.air_sdk.organization.Organization.refresh')
    def test_remove_member(self, mock_refresh):
        username = 'user1@nvidia.com'
        self.model.remove_member(username)
        self.api.client.delete.assert_called_once_with(self.model._members_api_url,
                                                       json={'username': username})
        mock_refresh.assert_called_once()
        mock_refresh.assert_called_once()

    @patch('air_sdk.air_sdk.organization.Organization.refresh')
    def test_remove_member_no_refresh(self, mock_refresh):
        username = 'user1@nvidia.com'
        self.model.remove_member(username, _refresh_when_done=False)
        self.api.client.delete.assert_called_once()
        mock_refresh.assert_not_called()

    @patch('air_sdk.air_sdk.organization.Organization.refresh')
    @patch('air_sdk.air_sdk.organization.Organization.remove_member')
    def test_remove_members(self, mock_remove, mock_refresh):
        members = ['user1@nvidia.com', 'user2@nvidia.com']
        self.model.remove_members(members)
        mock_for_assert = MagicMock()
        mock_for_assert(members[0], _refresh_when_done=False)
        mock_for_assert(members[1], _refresh_when_done=False)
        self.assertEqual(mock_remove.mock_calls, mock_for_assert.mock_calls)
        mock_refresh.assert_called_once()

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
        org_id = 'abc123'
        self.client.get.return_value.json.return_value = {'id': org_id, 'name': 'test'}
        res = self.api.get('abc123', foo='bar')
        self.client.get.assert_called_with(f'{self.client.api_url}/organization/abc123/',
                                           params={'foo': 'bar'})
        mock_raise.assert_called_with(self.client.get.return_value)
        self.assertIsInstance(res, organization.Organization)
        self.assertEqual(res.id, org_id)

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
