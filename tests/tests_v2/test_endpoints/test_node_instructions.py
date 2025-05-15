# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
import json
from http import HTTPStatus

import pytest
import faker

from air_sdk.v2.endpoints.mixins import serialize_payload

faker.Faker.seed(0)
fake = faker.Faker()


class TestNodeInstructionsEndpointApi:
    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({}, False),
            (
                {
                    'pk': fake.uuid4(cast_to=str),
                    'executor': fake.slug(),
                    'data': fake.slug(),
                    'monitor': fake.slug(),
                },
                False,
            ),
            (
                {
                    'pk': fake.uuid4(cast_to=str),
                    'executor': 'init',
                    'data': fake.slug(),
                    'monitor': fake.slug(),
                },
                True,
            ),
            (
                {
                    'pk': fake.uuid4(cast_to=str),
                    'executor': 'init',
                    'data': fake.slug(),
                },
                True,
            ),
        ),
    )
    def test_create(self, setup_mock_responses, api, node_instruction_factory, payload, is_valid):
        """This tests that the data provided is properly validated and used."""
        if is_valid:
            processed_payload = json.loads(serialize_payload(payload))
            expected_inst = node_instruction_factory(api.node_instructions.__api__, **processed_payload)
            setup_mock_responses(
                {
                    ('POST', api.node_instructions.url.format(id=payload['pk'])): {
                        'json': json.loads(expected_inst.json()),
                        'status_code': HTTPStatus.CREATED,
                    }
                }
            )
            inst = api.node_instructions.create(**payload)
            # Verify that the returned instance and the expected instance are equal
            assert inst == expected_inst
            # Verify that the returned instance and the expected instance are not the same
            assert inst is not expected_inst
        else:
            with pytest.raises(Exception) as err:
                api.node_instructions.create(**payload)
            assert err.type in (TypeError, ValueError)
