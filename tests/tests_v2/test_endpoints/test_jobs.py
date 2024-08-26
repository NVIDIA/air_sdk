# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

import pytest
import faker

faker.Faker.seed(0)
fake = faker.Faker()


class TestJobEndpointApi:
    def test_list(self, api, run_list_test, job_factory):
        run_list_test(api.jobs, job_factory)

    def test_job_worker_field(self, api, job_factory, worker_factory):
        assert job_factory(api).worker.__pk__ is not None
        assert job_factory(api, worker=None).worker is None
        assert job_factory(api, worker=worker_factory(api)).worker.__pk__ is not None

    def test_refresh(self, api, run_refresh_test, job_factory):
        run_refresh_test(api.jobs, job_factory)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({}, False),
            ({'fake_param': fake.slug()}, False),
            ({'state': fake.pyint()}, False),
            ({'state': None}, False),
            ({'state': False}, False),
            ({'state': 'COMPLETE'}, True),
            ({'state': 'FAILED'}, True),
            ({'state': 'WORKING'}, True),
        ),
    )
    def test_update(self, api, run_update_patch_test, job_factory, payload, is_valid):
        run_update_patch_test(api.jobs, job_factory, payload, is_valid)
