# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
import json
from http import HTTPStatus

import pytest
from air_sdk.exceptions import AirUnexpectedResponse
import faker

faker.Faker.seed(0)
fake = faker.Faker()


class TestInterfaceEndpointApi:
    def test_list(self, api, run_list_test, interface_factory):
        run_list_test(api.interfaces, interface_factory)

    def test_link_lazy_attribute(self, setup_mock_responses, api, interface_factory, link_factory):
        link_uuid = str(fake.uuid4())
        interface = interface_factory(api, link=link_uuid)
        results = [json.loads(link_factory(api, id=link_uuid).json())]
        setup_mock_responses(
            {
                ('GET', api.links.url): {
                    'json': {'previous': None, 'next': None, 'count': len(results), 'results': results},
                    'status_code': HTTPStatus.OK,
                }
            }
        )
        assert str(interface.link.id) == link_uuid

    def test_refresh(self, api, run_refresh_test, interface_factory):
        run_refresh_test(api.interfaces, interface_factory)

    def test_delete(self, api, run_delete_test, interface_factory):
        run_delete_test(api.interfaces, interface_factory)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({}, False),
            ({'name': None, 'node': None}, False),
            ({'name': fake.slug(), 'node': None}, False),
            ({'name': None, 'node': fake.uuid4(cast_to=str)}, False),
            ({'name': fake.slug(), 'node': fake.uuid4(cast_to=str)}, True),
            ({'name': fake.slug(), 'node': fake.uuid4(cast_to=str), 'interface_type': None}, False),
            ({'name': fake.slug(), 'node': fake.uuid4(cast_to=str), 'interface_type': 'OOB_INTF'}, True),
            (
                {
                    'name': fake.slug(),
                    'node': fake.uuid4(cast_to=str),
                    'link_up': fake.pybool(),
                    'port_number': fake.port_number(),
                    'outbound': fake.pybool(),
                    'preserve_mac': fake.pybool(),
                    'mac_address': fake.mac_address(),
                    'internal_ipv4': fake.ipv4(),
                    'full_ipv6': fake.ipv6(),
                    'prefix_ipv6': fake.ipv6(),
                    'link': fake.uuid4(cast_to=str),
                },
                True,
            ),
            (
                {
                    'name': fake.slug(),
                    'node': fake.uuid4(cast_to=str),
                    'link': fake.pybool(),
                },
                False,
            ),
        ),
    )
    def test_create(self, api, setup_mock_responses, interface_factory, payload, is_valid):
        """This tests that the data provided is properly validated and used."""
        endpoint_api = api.interfaces
        if is_valid:
            factory_kwargs = {k: v for k, v in payload.items() if v is not None}
            expected_inst = interface_factory(endpoint_api.__api__, **factory_kwargs)
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
            with pytest.raises(Exception) as err:
                endpoint_api.create(**payload)
            assert err.type in (TypeError, ValueError)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            # Empty case
            ({}, True),
            # Valid data cases
            ({'name': fake.slug()}, True),
            ({'port_number': fake.port_number()}, True),
            ({'outbound': fake.pybool()}, True),
            ({'link_up': fake.pybool()}, True),
            ({'preserve_mac': fake.pybool()}, True),
            ({'link': fake.uuid4(cast_to=None)}, True),
            ({'link': fake.uuid4(cast_to=str)}, True),
            ({'link': 'use_real_link'}, True),
            # None cases
            ({'name': None}, True),
            ({'port_number': None}, True),
            ({'outbound': None}, True),
            ({'link_up': None}, True),
            ({'preserve_mac': None}, True),
            ({'link': None}, True),
            # Invalid data type cases
            ({'name': fake.pyint()}, False),
            ({'port_number': fake.slug()}, False),
            ({'outbound': fake.slug()}, False),
            ({'link_up': fake.slug}, False),
            ({'preserve_mac': fake.slug()}, False),
            ({'link': fake.pyint()}, False),
        ),
    )
    def test_update(self, api, run_update_patch_test, interface_factory, link_factory, payload, is_valid):
        if payload.get('link') == 'use_real_link':
            payload['link'] = link_factory(api)
        run_update_patch_test(api.interfaces, interface_factory, payload, is_valid)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            # Empty case
            ({}, False),
            (
                {
                    'name': fake.slug(),
                    'port_number': fake.port_number(),
                    'outbound': fake.pybool(),
                    'preserve_mac': fake.pybool(),
                    'link_up': fake.pybool(),
                    'link': 'use_real_link',
                },
                True,
            ),
            (
                {
                    'name': fake.slug(),
                    'port_number': fake.port_number(),
                    'outbound': fake.pybool(),
                    'preserve_mac': fake.pybool(),
                    'link_up': fake.pybool(),
                    'link': fake.uuid4(cast_to=None),
                },
                True,
            ),
            (
                {
                    'name': fake.slug(),
                    'port_number': fake.port_number(),
                    'outbound': fake.pybool(),
                    'preserve_mac': fake.pybool(),
                    'link_up': fake.pybool(),
                    'link': fake.uuid4(cast_to=str),
                },
                True,
            ),
            (
                {
                    'name': fake.slug(),
                    'port_number': fake.port_number(),
                    'outbound': fake.pybool(),
                    'preserve_mac': fake.pybool(),
                    'link_up': fake.pybool(),
                    'link': None,
                },
                True,
            ),
            (
                {
                    'name': fake.slug(),
                    'port_number': fake.port_number(),
                    'outbound': fake.pybool(),
                    'preserve_mac': fake.slug(),
                    'link_up': fake.pybool(),
                    'link': None,
                },
                False,
            ),
            (
                {
                    'name': fake.slug(),
                    'port_number': fake.port_number(),
                    'outbound': fake.pybool(),
                    'preserve_mac': fake.pybool(),
                    'link_up': fake.pybool(),
                },
                False,
            ),
        ),
    )
    def test_full_update(
        self, api, run_full_update_patch_test, interface_factory, link_factory, payload, is_valid
    ):
        if payload.get('link') == 'use_real_link':
            payload['link'] = link_factory(api)
        run_full_update_patch_test(api.interfaces, interface_factory, payload, is_valid)

    def test_interface_breakout(self, api, interface_factory, breakout_factory, setup_mock_responses):
        instance = interface_factory(api.interfaces.__api__)
        breakout_detail_url = api.breakouts.url

        # Test valid cases
        for split_count in [2, 4]:
            expected_breakout = breakout_factory(api.breakouts.__api__, split_count=split_count)
            setup_mock_responses(
                {
                    ('POST', breakout_detail_url): {
                        'json': json.loads(expected_breakout.json()),
                        'status_code': HTTPStatus.CREATED,
                    },
                }
            )
            breakout_response = instance.breakout(split_count=split_count)
            assert breakout_response.id == expected_breakout.id
            assert breakout_response.name == expected_breakout.name
            assert breakout_response.split_count == expected_breakout.split_count

        # Test invalid cases
        for invalid_split_count in [1, 5, 'invalid', None]:
            setup_mock_responses(
                {
                    ('POST', breakout_detail_url): {
                        'json': {'error': 'Invalid request'},
                        'status_code': HTTPStatus.BAD_REQUEST,
                    },
                }
            )
            with pytest.raises(Exception) as err:
                instance.breakout(split_count=invalid_split_count)
            assert err.type in (AirUnexpectedResponse, TypeError, ValueError)
