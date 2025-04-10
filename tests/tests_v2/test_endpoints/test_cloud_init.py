# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
import json
from http import HTTPStatus

import faker
import pytest

from air_sdk.v2.endpoints.mixins import serialize_payload
from air_sdk.v2.utils import join_urls

faker.Faker.seed(0)
fake = faker.Faker()


class TestCloudInit:
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


class TestCloudInitEndpointApi:
    def test_bulk_assign(self, api, mock_client, node_factory, user_config_factory):
        node_1, node_2 = node_factory(api), node_factory(api)
        user_data, meta_data = user_config_factory(api), user_config_factory(api)
        assignments = [
            {'simulation_node': node_1.id, 'user_data': user_data.id},
            {'simulation_node': node_2.id, 'user_data': None, 'meta_data': meta_data.id},
        ]
        payload = serialize_payload(assignments)
        patch_called = False

        def _validate_payload(request, *args, **kwargs):
            """Makes sure a call was made and proper payload was provided."""
            nonlocal patch_called
            assert payload == request.text
            patch_called = True
            return None

        mock_client.register_uri(
            'PATCH',
            join_urls(api.client.base_url, api.cloud_inits.BULK_API_PATH),
            json=_validate_payload,
            status_code=HTTPStatus.NO_CONTENT,
        )
        api.cloud_inits.bulk_assign(assignments)
        assert patch_called is True
