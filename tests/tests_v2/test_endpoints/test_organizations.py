# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from http import HTTPStatus
import uuid
from dataclasses import is_dataclass

import pytest
import faker

from air_sdk.v2.endpoints.organizations import OrganizationMembersEndpointApi
from air_sdk.v2.exceptions import AirModelAttributeError

faker.Faker.seed(0)
fake = faker.Faker()


class TestOrganizationEndpointApi:
    def test_list(self, api, run_list_test, organization_factory):
        run_list_test(api.organizations, organization_factory)

    def test_refresh(self, api, run_refresh_test, organization_factory):
        run_refresh_test(api.organizations, organization_factory)

    def test_org_dom(self, api, organization_factory):
        org = organization_factory(api)
        assert len(org.name) >= 0
        assert isinstance(org.member_count, int)
        # Ensure access to the resource budget works
        rb = org.resource_budget
        assert is_dataclass(rb)
        assert uuid.UUID(rb.id) is not None, 'resource budget has valid uuid'
        assert rb.cpu >= rb.cpu_used

    @pytest.mark.parametrize(
        'resource_budget,is_valid',
        (
            (None, False),
            (fake.uuid4(cast_to=None), True),
            (fake.uuid4(cast_to=str), True),
            (fake.pyint(), False),
            (fake.slug(), False),
            ('use_factory', True),
            ({'id': str(fake.uuid4(cast_to=str))}, True),
        ),
    )
    def test_resource_budget_access(
        self, api, organization_factory, resource_budget_factory, resource_budget, is_valid
    ):
        if is_valid:
            if resource_budget == 'use_factory':
                resource_budget = resource_budget_factory(api)
            org = organization_factory(api, resource_budget=resource_budget)
            assert org.resource_budget.id is not None
        else:
            with pytest.raises(Exception) as err:
                organization_factory(api, resource_budget=resource_budget)
            assert err.type == AirModelAttributeError

    def test_organization_list_members(self, setup_mock_responses, api, organization_factory):
        """Test listing organization members"""
        org = organization_factory(api)
        endpoint_api = OrganizationMembersEndpointApi(api)

        # Create mock member data
        mock_members = [
            {
                'id': str(fake.uuid4()),
                'username': fake.user_name(),
                'roles': ['admin', 'member'],
                'resource_budget': {
                    'id': str(fake.uuid4()),
                    'cpu': 100,
                    'cpu_used': 50,
                    'memory': 1024,
                    'memory_used': 512,
                },
            },
            {
                'id': str(fake.uuid4()),
                'username': fake.user_name(),
                'roles': ['member'],
                'resource_budget': {
                    'id': str(fake.uuid4()),
                    'cpu': 200,
                    'cpu_used': 100,
                    'memory': 2048,
                    'memory_used': 1024,
                },
            },
        ]

        # Mock the endpoint response
        setup_mock_responses(
            {
                ('GET', endpoint_api.url.format(id=org.id)): {
                    'json': {
                        'previous': None,
                        'next': None,
                        'count': len(mock_members),
                        'results': mock_members,
                    },
                    'status_code': HTTPStatus.OK,
                }
            }
        )

        # Get members and verify
        members = list(org.list_members())
        assert len(members) == len(mock_members)

        # Verify each member's attributes
        for member, mock_data in zip(members, mock_members):
            assert member.id == mock_data['id']
            assert member.username == mock_data['username']
            assert member.roles == mock_data['roles']
            assert member.resource_budget.id == mock_data['resource_budget']['id']
            assert member.resource_budget.cpu == mock_data['resource_budget']['cpu']
            assert member.resource_budget.cpu_used == mock_data['resource_budget']['cpu_used']
            assert member.resource_budget.memory == mock_data['resource_budget']['memory']
            assert member.resource_budget.memory_used == mock_data['resource_budget']['memory_used']


class TestOrganizationMemberApi:
    def test_list_members_success(self, setup_mock_responses, api):
        """Test successful retrieval of organization members"""
        endpoint_api = OrganizationMembersEndpointApi(api)
        org_id = fake.uuid4(cast_to=str)

        # Create mock member data
        mock_members = [
            {
                'id': str(fake.uuid4()),
                'username': fake.user_name(),
                'roles': ['admin', 'member'],
                'resource_budget': {
                    'id': str(fake.uuid4()),
                    'cpu': 100,
                    'cpu_used': 50,
                    'memory': 1024,
                    'memory_used': 512,
                },
            },
            {
                'id': str(fake.uuid4()),
                'username': fake.user_name(),
                'roles': ['member'],
                'resource_budget': {
                    'id': str(fake.uuid4()),
                    'cpu': 200,
                    'cpu_used': 100,
                    'memory': 2048,
                    'memory_used': 1024,
                },
            },
        ]

        # Mock the endpoint response
        setup_mock_responses(
            {
                ('GET', endpoint_api.url.format(id=org_id)): {
                    'json': {
                        'previous': None,
                        'next': None,
                        'count': len(mock_members),
                        'results': mock_members,
                    },
                    'status_code': HTTPStatus.OK,
                }
            }
        )

        # Convert generator to list for validation
        instances = list(endpoint_api.list_organization_members(organization=org_id))

        # Validate the results
        assert len(instances) == len(mock_members), 'Number of returned instances should match mock data'

        # Validate each instance against corresponding mock data
        for instance, mock_data in zip(instances, mock_members):
            # Validate basic fields
            assert instance.id == mock_data['id'], 'Member ID should match'
            assert instance.username == mock_data['username'], 'Username should match'
            assert instance.roles == mock_data['roles'], 'Roles should match'

            # Validate resource budget
            assert (
                instance.resource_budget.id == mock_data['resource_budget']['id']
            ), 'Resource budget ID should match'
            assert (
                instance.resource_budget.cpu == mock_data['resource_budget']['cpu']
            ), 'CPU allocation should match'
            assert (
                instance.resource_budget.cpu_used == mock_data['resource_budget']['cpu_used']
            ), 'CPU usage should match'
            assert (
                instance.resource_budget.memory == mock_data['resource_budget']['memory']
            ), 'Memory allocation should match'
            assert (
                instance.resource_budget.memory_used == mock_data['resource_budget']['memory_used']
            ), 'Memory usage should match'

    def test_list_members_empty_results(self, setup_mock_responses, api):
        """Test when organization has no members"""
        endpoint_api = OrganizationMembersEndpointApi(api)
        org_id = fake.uuid4(cast_to=str)

        # Create mock member data
        mock_members = []

        # Mock the endpoint response
        setup_mock_responses(
            {
                ('GET', endpoint_api.url.format(id=org_id)): {
                    'json': {
                        'previous': None,
                        'next': None,
                        'count': len(mock_members),
                        'results': mock_members,
                    },
                    'status_code': HTTPStatus.OK,
                }
            }
        )

        instances = list(endpoint_api.list_organization_members(organization=org_id))
        assert len(instances) == 0
