# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
import json
from datetime import timezone

import pytest
import faker

faker.Faker.seed(0)
fake = faker.Faker()


class TestSimulationEndpointApi:
    def test_list(self, api, run_list_test, simulation_factory):
        run_list_test(api.simulations, simulation_factory)

    def test_refresh(self, api, run_refresh_test, simulation_factory):
        run_refresh_test(api.simulations, simulation_factory)

    def test_delete(self, api, run_delete_test, simulation_factory):
        run_delete_test(api.simulations, simulation_factory)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({}, False),
            ({'title': None}, False),
            ({'title': fake.company()}, True),
            ({'title': fake.company(), 'random_field': fake.slug()}, False),
            (
                {
                    'title': fake.company(),
                    'documentation': fake.url(),
                    'expires': fake.pybool(),
                    'expires_at': fake.date_time(tzinfo=timezone.utc),
                    'organization': fake.uuid4(cast_to=str),
                    'metadata': json.dumps(fake.pydict(value_types=(str,))),
                    'owner': fake.email(),
                    'preferred_worker': fake.uuid4(cast_to=str),
                    'sleep': fake.pybool(),
                    'sleep_at': fake.date_time(tzinfo=timezone.utc),
                },
                True,
            ),
            ({'title': fake.company(), 'preferred_worker': fake.pyint()}, False),
            ({'title': fake.company(), 'organization': fake.pyint()}, False),
        ),
    )
    def test_create(self, api, simulation_factory, run_create_test_case, payload, is_valid):
        """This tests that the data provided is properly validated and used."""
        run_create_test_case(api.simulations, simulation_factory, payload, is_valid)

    def test_update(self, api, run_update_patch_test, simulation_factory, worker_factory):
        cases = (
            # Empty Case
            ({}, True),
            # None cases
            ({'documentation': None}, True),
            ({'expires': None}, True),
            ({'expires_at': None}, True),
            ({'metadata': None}, True),
            ({'preferred_worker': None}, True),
            ({'sleep': None}, True),
            ({'sleep_at': None}, True),
            ({'title': None}, True),
            # Valid data cases
            ({'documentation': fake.url()}, True),
            ({'documentation': fake.slug()}, True),
            ({'expires': fake.pybool()}, True),
            ({'expires_at': fake.date_time(tzinfo=timezone.utc)}, True),
            ({'metadata': json.dumps(fake.pydict(value_types=(str,)))}, True),
            ({'metadata': ''}, True),
            ({'preferred_worker': fake.uuid4(cast_to=str)}, True),
            ({'preferred_worker': fake.uuid4(cast_to=None)}, True),
            ({'preferred_worker': worker_factory(api)}, True),
            ({'sleep': fake.pybool()}, True),
            ({'sleep_at': fake.date_time(tzinfo=timezone.utc)}, True),
            ({'title': fake.company()}, True),
            ({'title': fake.uuid4(cast_to=str)}, True),
            # Invalid data cases
            ({'documentation': fake.pybool()}, False),
            ({'documentation': fake.pyint()}, False),
            ({'expires': fake.slug()}, False),
            ({'expires_at': fake.pybool()}, False),
            ({'metadata': fake.pydict(value_types=(str,))}, False),
            ({'metadata': fake.pybool()}, False),
            ({'preferred_worker': fake.pybool()}, False),
            ({'sleep': fake.slug()}, False),
            ({'sleep_at': fake.slug()}, False),
            ({'sleep_at': fake.pybool()}, False),
            ({'title': fake.pybool()}, False),
            ({'title': fake.pyint()}, False),
            ({'title': fake.uuid4(cast_to=None)}, False),
            # Unexpected field case
            ({fake.slug().replace('-', '_'): fake.slug()}, False),
        )
        for payload, is_valid in cases:
            run_update_patch_test(api.simulations, simulation_factory, payload, is_valid)

    def test_full_update(self, api, run_full_update_patch_test, simulation_factory, worker_factory):
        cases = (
            # Empty Case
            ({}, False),
            # Minimal data case
            (
                {
                    'documentation': None,
                    'expires': fake.pybool(),
                    'expires_at': fake.date_time(tzinfo=timezone.utc),
                    'metadata': None,
                    'preferred_worker': None,
                    'sleep': fake.pybool(),
                    'sleep_at': fake.date_time(tzinfo=timezone.utc),
                    'title': fake.company(),
                },
                True,
            ),
            # Full data cases
            (
                {
                    'documentation': fake.url(),
                    'expires': fake.pybool(),
                    'expires_at': fake.date_time(tzinfo=timezone.utc),
                    'metadata': json.dumps(fake.pydict(value_types=(str,))),
                    'preferred_worker': worker_factory(api),
                    'sleep': fake.pybool(),
                    'sleep_at': fake.date_time(tzinfo=timezone.utc),
                    'title': fake.company(),
                },
                True,
            ),
            (
                {
                    'documentation': fake.url(),
                    'expires': fake.pybool(),
                    'expires_at': fake.date_time(tzinfo=timezone.utc),
                    'metadata': json.dumps(fake.pydict(value_types=(str,))),
                    'preferred_worker': fake.uuid4(cast_to=None),
                    'sleep': fake.pybool(),
                    'sleep_at': fake.date_time(tzinfo=timezone.utc),
                    'title': fake.company(),
                },
                True,
            ),
            # Unexpected field case
            (
                {
                    'documentation': None,
                    'expires': fake.pybool(),
                    'expires_at': fake.date_time(tzinfo=timezone.utc),
                    'metadata': None,
                    'preferred_worker': None,
                    'sleep': fake.pybool(),
                    'sleep_at': fake.date_time(tzinfo=timezone.utc),
                    'title': fake.company(),
                    fake.slug().replace('-', '_'): fake.slug(),
                },
                False,
            ),
            # Missing data cases
            (
                {
                    'documentation': fake.url(),
                    'expires': fake.pybool(),
                    'expires_at': fake.date_time(tzinfo=timezone.utc),
                    'metadata': json.dumps(fake.pydict(value_types=(str,))),
                    'sleep': fake.pybool(),
                    'sleep_at': fake.date_time(tzinfo=timezone.utc),
                    'title': fake.company(),
                },
                False,
            ),
        )
        for payload, is_valid in cases:
            run_full_update_patch_test(api.simulations, simulation_factory, payload, is_valid)
