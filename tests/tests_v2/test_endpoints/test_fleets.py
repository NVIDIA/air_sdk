# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from http import HTTPStatus
import json
from air_sdk.exceptions import AirUnexpectedResponse
import faker
import pytest

from air_sdk.v2.endpoints.mixins import serialize_payload
from air_sdk.v2.utils import join_urls

faker.Faker.seed(0)
fake = faker.Faker()


class TestFleetEndpointApi:
    def test_list(self, api, run_list_test, fleet_factory):
        run_list_test(api.fleets, fleet_factory)

    def test_refresh(self, api, run_refresh_test, fleet_factory):
        run_refresh_test(api.fleets, fleet_factory)

    def test_delete(self, api, run_delete_test, fleet_factory):
        run_delete_test(api.fleets, fleet_factory)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({}, False),  # Empty payload
            ({'name': None}, False),  # None name
            ({'name': ''}, False),  # Empty string name
            ({'name': ' '}, False),  # Whitespace name
            ({'name': fake.company()}, False),
            ({'name': fake.company(), 'organization': str(fake.uuid4(cast_to=str))}, True),
            (
                {
                    'name': fake.company(),
                    'prefix': fake.slug(),
                    'prefix_length': fake.pyint(),
                    'gateway_ipv4': fake.slug(),
                    'port_range': fake.slug(),
                    'container_ipv4_network': fake.slug(),
                    'container_prefix': fake.pyint(),
                    'organization': str(fake.uuid4(cast_to=str)),
                    'labels': [fake.slug()],
                },
                True,
            ),  # Full valid payload
            ({'name': 123}, False),  # Invalid name type
        ),
    )
    def test_create(self, api, fleet_factory, run_create_test_case, payload, is_valid):
        """Tests that the fleet data provided is properly validated and used."""
        run_create_test_case(api.fleets, fleet_factory, payload, is_valid)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            # Full update (PUT) test cases
            (
                {
                    'name': 'test-fleet',
                    'prefix': '192.168.1.0',
                    'prefix_length': 4294967295,
                    'gateway_ipv4': '192.168.1.1',
                    'port_range': '30000-32767',
                    'container_ipv4_network': '172.16.0.0',
                    'container_prefix': 4294967295,
                    'organization': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                    'labels': ['prod,test'],
                },
                True,
            ),  # Valid full payload
            ({}, False),  # Empty payload not allowed for full update
            (
                {
                    'name': 'test-fleet',  # Missing required fields
                    'prefix': '192.168.1.0',
                },
                False,
            ),
            (
                {
                    'name': fake.pyint(),  # invalid type
                    'prefix': '192.168.1.0',
                    'prefix_length': 4294967295,
                    'gateway_ipv4': '192.168.1.1',
                    'port_range': '30000-32767',
                    'container_ipv4_network': '172.16.0.0',
                    'container_prefix': 4294967295,
                    'organization': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                    'labels': ['prod,test'],
                },
                False,
            ),
            (
                {
                    'name': fake.slug(),  # invalid type
                    'prefix': '192.168.1.0',
                    'prefix_length': 4294967295,
                    'gateway_ipv4': '192.168.1.1',
                    'port_range': '30000-32767',
                    'container_ipv4_network': '172.16.0.0',
                    'container_prefix': 4294967295,
                    'organization': fake.pyint(),  # wrong type for organization
                    'labels': ['prod,test'],
                },
                False,
            ),
        ),
    )
    def test_full_update(self, api, fleet_factory, setup_mock_responses, payload, is_valid):
        endpoint_api = api.fleets
        instance = fleet_factory(endpoint_api.__api__)
        detail_url = join_urls(endpoint_api.url, str(instance.__pk__))

        if is_valid:
            processed_payload = json.loads(
                serialize_payload({k: v for k, v in payload.items() if v is not None})
            )
            updated_inst = fleet_factory(endpoint_api.__api__, **{**instance.dict(), **processed_payload})
            setup_mock_responses(
                {
                    ('PATCH', detail_url): {
                        'json': json.loads(instance.json()),
                        'status_code': HTTPStatus.OK,
                    },
                }
            )
            instance.full_update(**payload)
            assert instance == updated_inst
            assert instance is not updated_inst
        else:
            setup_mock_responses(
                {
                    ('PATCH', detail_url): {
                        'json': json.loads(instance.json()),
                        'status_code': HTTPStatus.BAD_REQUEST,
                    },
                }
            )
            with pytest.raises((TypeError, ValueError, AirUnexpectedResponse)):
                instance.full_update(**payload)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            # Partial update (PATCH) test cases
            ({}, True),  # Empty update is valid for PATCH
            ({'name': 'updated-fleet'}, True),  # Single field update
            ({'prefix': '192.168.2.0', 'prefix_length': 4294967295}, True),  # Multiple field update
            ({'gateway_ipv4': '192.168.2.1'}, True),  # Single network config update
            ({'port_range': '30000-32767'}, True),  # Update port range only
            ({'labels': ['prod,staging']}, True),  # Update labels only
            ({'name': None}, False),  # Cannot set name to None
            ({'prefix': 'invalid-ip'}, False),  # Invalid IP format
            ({'prefix_length': 4294967296}, False),  # Value exceeds maximum
            ({'port_range': 'invalid-range'}, False),  # Invalid port range format
            ({'organization': 'invalid-uuid'}, False),  # Invalid UUID format
            (
                {
                    'container_ipv4_network': '172.16.0.0',
                    'container_prefix': 'invalid',  # Invalid type
                },
                False,
            ),
        ),
    )
    def test_partial_update(self, api, fleet_factory, setup_mock_responses, payload, is_valid):
        endpoint_api = api.fleets
        instance = fleet_factory(endpoint_api.__api__)
        detail_url = join_urls(endpoint_api.url, str(instance.__pk__))

        if is_valid:
            processed_payload = json.loads(
                serialize_payload({k: v for k, v in payload.items() if v is not None})
            )
            updated_inst = fleet_factory(endpoint_api.__api__, **{**instance.dict(), **processed_payload})
            setup_mock_responses(
                {
                    ('PATCH', detail_url): {
                        'json': json.loads(instance.json()),
                        'status_code': HTTPStatus.OK,
                    },
                }
            )
            instance.update(**payload)
            assert instance == updated_inst
            assert instance is not updated_inst
        else:
            setup_mock_responses(
                {
                    ('PATCH', detail_url): {
                        'json': json.loads(instance.json()),
                        'status_code': HTTPStatus.BAD_REQUEST,
                    },
                }
            )
            with pytest.raises((TypeError, ValueError, AirUnexpectedResponse)):
                instance.update(**payload)
