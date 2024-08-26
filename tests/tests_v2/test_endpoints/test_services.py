# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT


import pytest
import faker

faker.Faker.seed(0)
fake = faker.Faker()


class TestServiceEndpointApi:
    def test_list(self, api, run_list_test, service_factory):
        run_list_test(api.services, service_factory)

    def test_delete(self, api, run_delete_test, service_factory):
        run_delete_test(api.services, service_factory)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({}, False),
            ({'name': None, 'dest_port': None, 'interface': None}, False),
            ({'name': fake.slug(), 'dest_port': fake.slug(), 'interface': fake.slug()}, False),
            (
                {
                    'name': fake.slug(),
                    'dest_port': fake.slug(),
                    'interface': fake.slug(),
                    'service_type': None,
                },
                False,
            ),
            (
                {
                    'name': fake.slug(),
                    'dest_port': fake.slug(),
                    'interface': fake.slug(),
                    'service_type': fake.pyint(),
                },
                False,
            ),
            ({'name': fake.slug(), 'dest_port': fake.pyint(), 'interface': fake.uuid4(cast_to=str)}, True),
            (
                {
                    'name': fake.slug(),
                    'dest_port': fake.pyint(),
                    'interface': fake.uuid4(cast_to=str),
                    'service_type': fake.slug(),
                },
                True,
            ),
        ),
    )
    def test_create(self, api, service_factory, run_create_test_case, payload, is_valid):
        """This tests that the data provided is properly validated and used."""
        run_create_test_case(api.services, service_factory, payload, is_valid)
