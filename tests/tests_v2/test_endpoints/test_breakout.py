# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
import json
from http import HTTPStatus

import pytest
from air_sdk.exceptions import AirUnexpectedResponse
import faker

faker.Faker.seed(0)
fake = faker.Faker()


class TestBreakoutEndpointApi:
    def test_list(self, api, run_list_test, breakout_factory):
        run_list_test(api.breakouts, breakout_factory)

    def test_refresh(self, api, run_refresh_test, breakout_factory):
        run_refresh_test(api.breakouts, breakout_factory)

    def test_delete(self, api, run_delete_test, breakout_factory):
        run_delete_test(api.breakouts, breakout_factory)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            # Invalid cases
            ({}, False),
            ({'interface': str(fake.uuid4())}, False),  # Missing split_count
            ({'split_count': 4}, False),  # Missing interface
            (
                {
                    'interface': 'not-a-uuid',  # Invalid UUID format
                    'split_count': 4,
                },
                False,
            ),
            (
                {
                    'interface': str(fake.uuid4()),
                    'split_count': fake.slug(),  # Wrong type
                },
                False,
            ),
            ({'interface': None, 'split_count': None}, False),
            ({'interface': None, 'split_count': fake.pyint()}, False),
            ({'interface': fake.uuid4(cast_to=str), 'split_count': None}, False),
            ({'interface': fake.uuid4(cast_to=str), 'split_count': 1}, False),
            # Valid cases
            ({'interface': fake.uuid4(cast_to=str), 'split_count': 2}, True),
            ({'interface': fake.uuid4(cast_to=str), 'split_count': 4}, True),
            # special marker for Interface instance
            ({'interface': 'USE_INTERFACE_INSTANCE', 'split_count': 4}, True),
        ),
    )
    def test_create(self, api, setup_mock_responses, breakout_factory, interface_factory, payload, is_valid):
        """This tests that the data provided is properly validated and used."""
        endpoint_api = api.breakouts

        if payload.get('interface') == 'USE_INTERFACE_INSTANCE':
            payload['interface'] = interface_factory(api)

        if is_valid:
            factory_kwargs = {k: v for k, v in payload.items() if v is not None}
            expected_inst = breakout_factory(endpoint_api.__api__, **factory_kwargs)
            setup_mock_responses(
                {
                    ('POST', endpoint_api.url): {
                        'json': json.loads(expected_inst.json()),
                        'status_code': HTTPStatus.CREATED,
                    }
                }
            )
            inst = endpoint_api.create(**payload)
            assert inst == expected_inst
            assert inst is not expected_inst
        else:
            setup_mock_responses(
                {
                    ('POST', endpoint_api.url): {
                        'json': {'error': 'Invalid request'},
                        'status_code': HTTPStatus.BAD_REQUEST,
                    }
                }
            )
            with pytest.raises(Exception) as err:
                endpoint_api.create(**payload)
            assert err.type in (AirUnexpectedResponse, TypeError, ValueError)
