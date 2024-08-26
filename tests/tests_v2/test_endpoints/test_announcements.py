# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

import faker
import pytest

faker.Faker.seed(0)
fake = faker.Faker()


class TestAnnouncementEndpointApi:
    def test_list(self, api, run_list_test, announcement_factory):
        run_list_test(api.announcements, announcement_factory)

    def test_delete(self, api, run_delete_test, announcement_factory):
        run_delete_test(api.announcements, announcement_factory)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({}, False),
            ({'severity': None}, False),
            ({'severity': None, 'message': None}, False),
            ({'severity': fake.slug()}, False),
            ({'severity': fake.slug(), 'message': None}, False),
            ({'severity': fake.slug(), 'message': fake.text()}, True),
            ({'severity': None, 'message': fake.text()}, False),
        ),
    )
    def test_create(self, api, announcement_factory, run_create_test_case, payload, is_valid):
        run_create_test_case(api.announcements, announcement_factory, payload, is_valid)
