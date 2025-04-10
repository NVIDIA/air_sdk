# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
import json
from http import HTTPStatus
from uuid import UUID

import pytest
import faker

from air_sdk.v2.utils import join_urls

faker.Faker.seed(0)
fake = faker.Faker()


class TestLinkEndpointApi:
    def test_list(self, setup_mock_responses, api, link_factory):
        endpoint_api = api.links
        results = [
            json.loads(link_factory(endpoint_api.__api__).json()),
            json.loads(link_factory(endpoint_api.__api__).json()),
        ]
        setup_mock_responses(
            {
                ('GET', endpoint_api.url): {
                    'json': {'previous': None, 'next': None, 'count': len(results), 'results': results},
                    'status_code': HTTPStatus.OK,
                }
            }
        )
        # Test SDK
        links = list(endpoint_api.list(simulation=fake.uuid4(cast_to=str), limit=len(results)))
        assert len(links) == len(results)
        assert isinstance(links[0], endpoint_api.model)
        for link in links:
            assert link.id is not None
            for sim_iface in link.simulation_interfaces:
                assert isinstance(sim_iface.__pk__, UUID)
                assert isinstance(sim_iface.__pk__, UUID)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({}, False),
            ({'simulation': None, 'links': None}, False),
            ({'simulation': fake.uuid4(cast_to=str), 'links': None}, False),
            ({'simulation': fake.uuid4(cast_to=str), 'links': []}, False),
            ({'simulation': fake.uuid4(cast_to=str), 'links': [fake.uuid4(cast_to=str)]}, False),
            (
                {
                    'simulation': fake.uuid4(cast_to=str),
                    'links': [{'simulation_interfaces': [fake.uuid4(cast_to=str), fake.uuid4(cast_to=str)]}],
                },
                True,
            ),
            (
                {
                    'simulation': fake.uuid4(cast_to=str),
                    'links': [{'simulation_interfaces': [fake.uuid4(cast_to=str), fake.uuid4(cast_to=str)]}],
                    'extra_field': fake.slug(),
                },
                False,
            ),
        ),
    )
    def test_bulk_create(self, setup_mock_responses, api, link_factory, payload, is_valid):
        endpoint_api = api.links
        if is_valid:
            payload_links = payload.get('links')
            payload_sim = payload.get('simulation')
            expected_links = [
                link_factory(api, simulation_interfaces=link_data['simulation_interfaces'])
                for link_data in payload_links
            ]
            setup_mock_responses(
                {
                    ('POST', join_urls(endpoint_api.url, 'bulk-create')): {
                        'json': (
                            {
                                'simulation': payload_sim,
                                'links': [json.loads(link.json()) for link in expected_links],
                            }
                        ),
                        'status_code': HTTPStatus.CREATED,
                    }
                }
            )
            created_links = endpoint_api.bulk_create(**payload)
            for created_link, expected_link in zip(created_links, expected_links):
                assert created_link == expected_link
                assert created_link is not expected_link
        else:
            with pytest.raises(Exception) as err:
                endpoint_api.bulk_create(**payload)
            assert err.type in (TypeError, ValueError)

    def test_bulk_delete(
        self, setup_mock_responses, api, simulation_factory, interface_factory, link_factory
    ):
        simulation_inst = simulation_factory(api)
        unsaved_sim = simulation_factory(api)
        setattr(unsaved_sim, unsaved_sim.primary_key_field, None)
        interface_inst = interface_factory(api)
        link_inst = link_factory(api)
        alt_link_inst = link_factory(api)
        cases = [
            ({}, False),
            ({'simulation': None, 'links': None}, False),
            ({'simulation': simulation_inst, 'links': simulation_inst}, False),
            ({'simulation': simulation_inst, 'links': []}, False),
            ({'simulation': simulation_inst, 'links': None}, True),
            ({'simulation': unsaved_sim, 'links': None}, False),
            ({'simulation': simulation_inst, 'links': [None]}, False),
            ({'simulation': simulation_inst, 'links': [fake.pyint()]}, False),
            ({'simulation': interface_inst, 'links': [fake.uuid4(cast_to=str)]}, False),
            ({'simulation': simulation_inst, 'links': [fake.uuid4(cast_to=str)]}, True),
            ({'simulation': simulation_inst.id, 'links': [fake.uuid4(cast_to=str)]}, True),
            ({'simulation': str(simulation_inst.id), 'links': [fake.uuid4(cast_to=str)]}, True),
            ({'simulation': simulation_inst, 'links': [fake.uuid4(cast_to=None)]}, True),
            ({'simulation': simulation_inst, 'links': [link_inst, alt_link_inst]}, True),
            (
                {
                    'simulation': simulation_inst,
                    'links': [fake.uuid4(cast_to=str), fake.uuid4(cast_to=None), link_inst],
                },
                True,
            ),
        ]
        for i, (params, is_valid) in enumerate(cases):
            failure_msg = f'Failed on case {i}'
            if is_valid:
                link_ids = params.get('links') or []
                setup_mock_responses(
                    {
                        ('DELETE', join_urls(api.links.url, 'bulk-delete')): {
                            'json': {'links_deleted': len(link_ids)},
                            'status_code': HTTPStatus.OK,
                        }
                    }
                )
                deletion_data = api.links.bulk_delete(**params)
                assert deletion_data['links_deleted'] == len(link_ids), failure_msg
            else:
                with pytest.raises(Exception) as err:
                    api.links.bulk_delete(**params)
                assert err.type in (TypeError, ValueError), failure_msg

    def test_get(self, setup_mock_responses, api, link_factory, simulation_factory):
        inst = link_factory(api)
        sim_inst = simulation_factory(api)

        # Set up mock client
        detail_url = join_urls(api.links.url, inst.id)
        setup_mock_responses(
            {
                ('GET', detail_url): {
                    'json': json.loads(inst.json()),
                    'status_code': HTTPStatus.OK,
                    'params': {'simulation': sim_inst.id},
                }
            }
        )

        link = api.links.get(pk=inst.id, simulation=sim_inst)  # Pass simulation instance
        assert link.dict() == inst.dict()

        link = api.links.get(pk=inst.id, simulation=sim_inst.id)  # Pass simulation ID
        assert link.dict() == inst.dict()

        # Test error cases
        none_url = join_urls(api.links.url, 'None')
        setup_mock_responses(
            {
                ('GET', none_url): {
                    'json': {'error': 'Invalid request'},
                    'status_code': HTTPStatus.BAD_REQUEST,
                    'params': {'simulation': sim_inst.id},
                }
            }
        )
        with pytest.raises(TypeError):
            api.links.get(pk=None, simulation=str(fake.uuid4()))

        test_id = str(fake.uuid4())
        detail_url = join_urls(api.links.url, test_id)
        setup_mock_responses(
            {
                ('GET', detail_url): {
                    'json': {'error': 'Invalid request'},
                    'status_code': HTTPStatus.BAD_REQUEST,
                    'params': {'simulation': None},
                }
            }
        )
        with pytest.raises(TypeError):
            api.links.get(pk=test_id, simulation=None)
