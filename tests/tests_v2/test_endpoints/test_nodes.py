# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
import json
from http import HTTPStatus

import pytest
import faker

from air_sdk.v2.utils import join_urls

faker.Faker.seed(0)
fake = faker.Faker()


class TestNodeEndpointApi:
    def test_list(self, api, run_list_test, node_factory):
        run_list_test(api.nodes, node_factory)

    def test_refresh(self, api, run_refresh_test, node_factory):
        run_refresh_test(api.nodes, node_factory)

    def test_delete(self, api, run_delete_test, node_factory):
        run_delete_test(api.nodes, node_factory)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({}, False),
            ({'simulation': None, 'name': None}, False),
            ({'simulation': fake.uuid4(cast_to=str), 'name': fake.slug()}, True),
            ({'simulation': fake.uuid4(cast_to=str), 'name': fake.slug(), 'pos_x': None}, False),
            (
                {
                    'simulation': fake.uuid4(cast_to=str),
                    'name': fake.slug(),
                    'pos_x': fake.pyfloat(min_value=-10, max_value=10),
                },
                True,
            ),
            (
                {
                    'simulation': fake.uuid4(cast_to=str),
                    'name': fake.slug(),
                    'boot_group': None,
                    'os': None,
                    'system': None,
                    'memory': None,
                    'cpu': None,
                    'storage': None,
                    'console_username': None,
                    'console_password': None,
                },
                True,
            ),
            (
                {
                    'simulation': fake.uuid4(cast_to=str),
                    'name': fake.slug(),
                    'boot_group': fake.pyint(),
                    'features': json.dumps(fake.pydict(value_types=(str,))),
                    'metadata': json.dumps(fake.pydict(value_types=(str,))),
                    'memory': fake.pyint(),
                    'storage': fake.pyint(),
                    'cpu': fake.pyint(),
                    'os': fake.uuid4(cast_to=str),
                    'system': fake.uuid4(cast_to=str),
                    'console_username': fake.uuid4(cast_to=str),
                    'console_password': fake.uuid4(cast_to=str),
                },
                True,
            ),
        ),
    )
    def test_create(self, api, node_factory, run_create_test_case, payload, is_valid):
        """This tests that the data provided is properly validated and used."""
        run_create_test_case(api.nodes, node_factory, payload, is_valid)

    def test_update(self, api, run_update_patch_test, node_factory):
        cases = (
            # Empty Case
            ({}, True),
            # None cases
            ({'name': None}, True),
            ({'state': None}, True),
            ({'pos_x': None}, True),
            ({'pos_y': None}, True),
            ({'boot_group': None}, True),
            ({'console_username': None}, True),
            ({'console_password': None}, True),
            ({'console_port': None}, True),
            ({'serial_port': None}, True),
            # Valid payload cases
            ({'name': fake.slug()}, True),
            ({'state': 'COMPLETE'}, True),
            ({'state': 'FAILURE'}, True),
            ({'pos_x': fake.pyfloat()}, True),
            ({'pos_y': fake.pyfloat()}, True),
            ({'boot_group': fake.pyint()}, True),
            ({'console_username': fake.uuid4(cast_to=str)}, True),
            ({'console_password': fake.uuid4(cast_to=str)}, True),
            ({'console_port': fake.port_number()}, True),
            ({'serial_port': fake.port_number()}, True),
            # Invalid values cases
            ({'name': fake.pyint()}, False),
            ({'state': fake.pybool()}, False),
            ({'pos_x': fake.slug()}, False),
            ({'pos_y': fake.slug()}, False),
            ({'boot_group': fake.slug()}, False),
            ({'console_username': fake.pyint()}, False),
            ({'console_password': fake.pyint()}, False),
            ({'console_port': fake.slug()}, False),
            ({'serial_port': fake.slug()}, False),
            # Unexpected payload value case
            ({fake.slug().replace('-', '_'): fake.slug()}, False),
        )
        for payload, is_valid in cases:
            run_update_patch_test(api.nodes, node_factory, payload, is_valid)

    def test_full_update(self, api, run_full_update_patch_test, node_factory):
        cases = (
            # Empty Case
            ({}, False),
            # Full valid data case
            (
                {
                    'name': fake.slug(),
                    'state': 'COMPLETE',
                    'pos_x': fake.pyfloat(),
                    'pos_y': fake.pyfloat(),
                    'boot_group': fake.pyint(),
                    'console_username': fake.uuid4(cast_to=str),
                    'console_password': fake.uuid4(cast_to=str),
                    'console_port': fake.port_number(),
                    'serial_port': fake.port_number(),
                },
                True,
            ),
            # Minimal valid data case
            (
                {
                    'name': fake.slug(),
                    'state': 'COMPLETE',
                    'pos_x': fake.pyfloat(),
                    'pos_y': fake.pyfloat(),
                    'boot_group': None,
                    'console_username': None,
                    'console_password': None,
                    'console_port': None,
                    'serial_port': None,
                },
                True,
            ),
            # Invalid None case
            (
                {
                    'name': None,
                    'state': None,
                    'pos_x': None,
                    'pos_y': None,
                    'boot_group': None,
                    'console_username': None,
                    'console_password': None,
                    'console_port': None,
                    'serial_port': None,
                },
                False,
            ),
            # Unexpected value case
            (
                {
                    'name': fake.slug(),
                    'state': 'COMPLETE',
                    'pos_x': fake.pyfloat(),
                    'pos_y': fake.pyfloat(),
                    'boot_group': None,
                    'console_username': None,
                    'console_password': None,
                    'console_port': None,
                    'serial_port': None,
                    fake.slug().replace('-', '_'): fake.slug(),
                },
                False,
            ),
        )
        for payload, is_valid in cases:
            run_full_update_patch_test(api.nodes, node_factory, payload, is_valid)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({}, False),
            ({'unexpected_key': fake.slug()}, False),
            ({'agent_key': fake.pyint()}, False),
            ({'agent_key': fake.slug()}, True),
            ({'agent_key': fake.uuid4(cast_to=str)}, True),
            ({'agent_key': None}, True),
        ),
    )
    def test_set_agent_key(self, api, setup_mock_responses, node_factory, payload, is_valid):
        endpoint_api = api.nodes
        model_factory = node_factory
        instance = model_factory(endpoint_api.__api__)
        response_data = {'json': json.loads(instance.json()), 'status_code': HTTPStatus.OK}
        method = instance.set_agent_key
        if is_valid:
            detail_url = join_urls(endpoint_api.url, str(instance.__pk__))
            setup_mock_responses({('PATCH', detail_url): response_data, ('GET', detail_url): response_data})
            method(**payload)
        else:
            with pytest.raises(Exception) as err:
                method(**payload)
            assert err.type in (TypeError, ValueError)

    def test_cloud_init(self, api, setup_mock_responses, node_factory, cloud_init_factory):
        node = node_factory(api)
        endpoint_api = api.cloud_inits
        url = endpoint_api.url.format(id=str(node.id))
        expected_inst = cloud_init_factory(api, simulation_node=node)
        updated_data = json.loads(expected_inst.json())
        updated_data['user_data'] = None
        updated_data['meta_data'] = None
        setup_mock_responses(
            {
                ('GET', url): {'json': json.loads(expected_inst.json()), 'status_code': HTTPStatus.OK},
                ('PATCH', url): {'json': updated_data, 'status_code': HTTPStatus.OK},
            },
        )
        cloud_init = node.cloud_init
        assert str(cloud_init.simulation_node.__pk__) == str(node.__pk__)
        assert cloud_init.user_data is not None
        assert cloud_init.meta_data is not None
        cloud_init.full_update(user_data=None, meta_data=None)
        assert cloud_init.user_data is None
        assert cloud_init.meta_data is None