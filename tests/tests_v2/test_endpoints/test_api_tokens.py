# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

import faker
import pytest

faker.Faker.seed(0)
fake = faker.Faker()


class TestApiTokenEndpointApi:
    def test_list(self, api, run_list_test, api_token_factory):
        run_list_test(api.api_tokens, api_token_factory)

    def test_delete(self, api, run_delete_test, api_token_factory):
        run_delete_test(api.api_tokens, api_token_factory)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({'name': None}, False),
            ({}, False),
            ({'random_key': fake.slug()}, False),
            ({'name': fake.slug()}, True),
            ({'name': fake.slug(), 'random_key': None}, False),
            ({'name': fake.slug(), 'expiry': None}, True),
            ({'name': fake.slug(), 'expiry': fake.date_time()}, True),
        ),
    )
    def test_create(self, api, api_token_factory, run_create_test_case, payload, is_valid):
        """This tests that the data provided is properly validated and used."""
        run_create_test_case(api.api_tokens, api_token_factory, payload, is_valid)
