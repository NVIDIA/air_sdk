# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
import json
from http import HTTPStatus

import pytest
import faker

from air_sdk.v2.endpoints.mixins import serialize_payload

faker.Faker.seed(0)
fake = faker.Faker()


class TestCloudInitEndpointApi:
    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            # Empty case
            ({}, False),
            ({'user_data': None, 'meta_data': None}, True),
            ({'user_data': fake.pybool(), 'meta_data': None}, False),
            ({'user_data': fake.uuid4(cast_to=None), 'meta_data': fake.uuid4(cast_to=None)}, True),
            ({'user_data': fake.uuid4(cast_to=None), 'meta_data': None}, True),
            ({'user_data': None, 'meta_data': fake.uuid4(cast_to=None)}, True),
            (
                {
                    'user_data': fake.uuid4(cast_to=None),
                    'meta_data': fake.uuid4(cast_to=None),
                    'unexpected_field': fake.uuid4(cast_to=None),
                },
                False,
            ),
        ),
    )
    def test_full_update(
        self, setup_mock_responses, api, run_full_update_patch_test, cloud_init_factory, payload, is_valid
    ):
        endpoint_api = api.cloud_inits
        instance = cloud_init_factory(endpoint_api.__api__)
        if is_valid:
            processed_payload = json.loads(serialize_payload(payload))
            updated_inst = cloud_init_factory(
                endpoint_api.__api__, **{**instance.dict(), **processed_payload}
            )
            detail_url = endpoint_api.url.format(id=str(instance.__pk__))
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
            with pytest.raises(Exception) as err:
                instance.full_update(**payload)
            assert err.type in (TypeError, ValueError)
