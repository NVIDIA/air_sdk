# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
import json
import uuid
from http import HTTPStatus

import pytest
import faker

from air_sdk import v2


faker.Faker.seed(0)
fake = faker.Faker()


class TestMarketplaceDemoEndpointApi:
    def setup_method(self):
        self.AirApi = v2.AirApi
        self.api_url = 'https://air-fake-test.nvidia.com/api/'
        self.api = v2.AirApi(api_url=self.api_url, authenticate=False)
        self.endpoint_url = v2.utils.join_urls(self.api_url, 'v2', self.api.marketplace_demos.API_PATH)

    def test_get(self, setup_mock_responses, marketplace_demo_factory):
        inst = marketplace_demo_factory(self.api)
        # Set up mock client
        detail_url = v2.utils.join_urls(self.endpoint_url, inst.id)
        expected_responses = {
            ('GET', detail_url): {
                'json': json.loads(inst.json()),  # Create a response representing the current inst
                'status_code': 200,
            }
        }
        setup_mock_responses(expected_responses)
        # Test SDK
        marketplace_demo = self.api.marketplace_demos.get(pk=inst.id)
        assert marketplace_demo.dict() == inst.dict()

    def test_lazy_snapshot(self, setup_mock_responses, marketplace_demo_factory, simulation_factory):
        sim = simulation_factory(self.api)
        inst = marketplace_demo_factory(self.api, snapshot=str(sim.id))
        assert hasattr(inst, 'snapshot')
        assert isinstance(inst.snapshot, v2.air_model.ForeignKeyMixin)
        assert inst.snapshot.__fk_resolved__ is False
        snapshot_pk = inst.snapshot.__pk__
        assert isinstance(snapshot_pk, uuid.UUID)

        # Set up mock client for resolution of lazy snapshot field
        simulation_details_url = v2.utils.join_urls(self.api.simulations.url, str(snapshot_pk))
        setup_mock_responses(
            {
                ('GET', simulation_details_url): {
                    'json': json.loads(sim.json()),
                    'status_code': HTTPStatus.OK,
                }
            }
        )
        assert inst.snapshot.dict() == sim.dict()

    def test_delete(self, api, run_delete_test, marketplace_demo_factory):
        run_delete_test(api.marketplace_demos, marketplace_demo_factory)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({}, False),
            ({'name': None, 'snapshot': None}, False),
            ({'name': fake.name(), 'snapshot': None}, False),
            ({'name': None, 'snapshot': fake.uuid4(cast_to=str)}, False),
            ({'name': fake.name(), 'snapshot': fake.uuid4(cast_to=str)}, True),
            ({'name': fake.name(), 'snapshot': fake.uuid4(cast_to=str), 'published': True}, True),
            (
                {
                    'name': fake.name(),
                    'snapshot': fake.uuid4(cast_to=str),
                    'tags': '',
                },
                False,
            ),
            (
                {
                    'name': fake.name(),
                    'snapshot': fake.uuid4(cast_to=str),
                    'published': True,
                    'documentation': fake.url(),
                    'description': fake.text(),
                    'repo': fake.url(),
                    'icon': fake.url(),
                    'owner': fake.uuid4(cast_to=str),
                    'tags': fake.pylist(value_types=(str,)),
                },
                True,
            ),
        ),
    )
    def test_create(self, api, marketplace_demo_factory, run_create_test_case, payload, is_valid):
        run_create_test_case(api.marketplace_demos, marketplace_demo_factory, payload, is_valid)

    def test_refresh(self, api, run_refresh_test, marketplace_demo_factory):
        run_refresh_test(api.marketplace_demos, marketplace_demo_factory)

    def test_update(
        self,
        api,
        run_update_patch_test,
        marketplace_demo_factory,
        marketplace_demo_tag_factory,
        simulation_factory,
    ):
        cases = (
            ({}, True),
            ({'name': None}, True),
            ({'name': fake.slug()}, True),
            ({'name': fake.pyint()}, False),
            ({'snapshot': None}, True),
            ({'snapshot': fake.uuid4(cast_to=str)}, True),
            ({'snapshot': fake.uuid4(cast_to=None)}, True),
            ({'snapshot': simulation_factory(api)}, True),
            ({'snapshot': fake.pybool()}, False),
            ({'snapshot': fake.pyint()}, False),
            ({'description': None}, True),
            ({'description': fake.text()}, True),
            ({'description': fake.pyint()}, False),
            ({'documentation': None}, True),
            ({'documentation': fake.url()}, True),
            ({'documentation': fake.slug()}, True),
            ({'documentation': fake.pybool()}, False),
            ({'repo': None}, True),
            ({'repo': fake.url()}, True),
            ({'repo': fake.slug()}, True),
            ({'repo': fake.pyint()}, False),
            ({'icon': None}, True),
            ({'icon': fake.text()}, True),
            ({'icon': fake.pyint()}, False),
            ({'owner': None}, True),
            ({'owner': fake.uuid4(cast_to=None)}, True),
            ({'owner': fake.uuid4(cast_to=str)}, True),
            ({'owner': fake.pyint()}, False),
            ({'tags': None}, True),
            ({'tags': []}, True),
            ({'tags': fake.pylist(value_types=(str,))}, True),
            ({'tags': [marketplace_demo_tag_factory(api)]}, True),
            ({'tags': [marketplace_demo_tag_factory(api) for _ in range(3)]}, True),
            ({'tags': [simulation_factory(api)]}, False),
            ({'published': None}, True),
            ({'published': fake.pybool()}, True),
            ({'published': fake.slug()}, False),
        )
        for payload, is_valid in cases:
            run_update_patch_test(api.marketplace_demos, marketplace_demo_factory, payload, is_valid)

    def test_full_update(
        self,
        api,
        run_full_update_put_test,
        marketplace_demo_factory,
        marketplace_demo_tag_factory,
        simulation_factory,
    ):
        cases = (
            ({}, False),
            (
                {
                    'name': fake.slug(),
                    'snapshot': fake.uuid4(cast_to=str),
                    'description': None,
                    'documentation': None,
                    'repo': None,
                    'icon': None,
                    'owner': None,
                    'tags': None,
                    'published': None,
                },
                False,
            ),
            (
                {
                    'name': fake.slug(),
                    'snapshot': fake.uuid4(cast_to=str),
                    'description': fake.text(),
                    'documentation': fake.url(),
                    'repo': fake.url(),
                    'icon': fake.text(),
                    'owner': fake.uuid4(cast_to=str),
                    'tags': fake.pylist(value_types=(str,)),
                    'published': fake.pybool(),
                },
                True,
            ),
            (
                {
                    'name': fake.slug(),
                    'snapshot': fake.uuid4(cast_to=str),
                    'description': None,
                    'documentation': None,
                    'repo': None,
                    'icon': None,
                    'owner': fake.uuid4(cast_to=str),
                    'tags': fake.pylist(value_types=(str,)),
                    'published': fake.pybool(),
                },
                True,
            ),
            (
                {
                    'name': fake.slug(),
                    'snapshot': simulation_factory(api),
                    'description': fake.text(),
                    'documentation': fake.url(),
                    'repo': fake.url(),
                    'icon': fake.text(),
                    'owner': fake.uuid4(cast_to=None),
                    'tags': [marketplace_demo_tag_factory(api) for _ in range(3)],
                    'published': fake.pybool(),
                },
                True,
            ),
        )
        for payload, is_valid in cases:
            run_full_update_put_test(api.marketplace_demos, marketplace_demo_factory, payload, is_valid)
