# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
import uuid
from dataclasses import is_dataclass

import pytest
import faker

from air_sdk.v2.exceptions import AirModelAttributeError

faker.Faker.seed(0)
fake = faker.Faker()


class TestOrganizationEndpointApi:
    def test_list(self, api, run_list_test, organization_factory):
        run_list_test(api.organizations, organization_factory)

    def test_refresh(self, api, run_refresh_test, organization_factory):
        run_refresh_test(api.organizations, organization_factory)

    def test_org_dom(self, api, organization_factory):
        org = organization_factory(api)
        assert len(org.name) >= 0
        assert isinstance(org.member_count, int)
        # Ensure access to the resource budget works
        rb = org.resource_budget
        assert is_dataclass(rb)
        assert uuid.UUID(rb.id) is not None, 'resource budget has valid uuid'
        assert rb.cpu >= rb.cpu_used

    @pytest.mark.parametrize(
        'resource_budget,is_valid',
        (
            (None, False),
            (fake.uuid4(cast_to=None), True),
            (fake.uuid4(cast_to=str), True),
            (fake.pyint(), False),
            (fake.slug(), False),
            ('use_factory', True),
            ({'id': str(fake.uuid4(cast_to=str))}, True),
        ),
    )
    def test_resource_budget_access(
        self, api, organization_factory, resource_budget_factory, resource_budget, is_valid
    ):
        if is_valid:
            if resource_budget == 'use_factory':
                resource_budget = resource_budget_factory(api)
            org = organization_factory(api, resource_budget=resource_budget)
            assert org.resource_budget.id is not None
        else:
            with pytest.raises(Exception) as err:
                organization_factory(api, resource_budget=resource_budget)
            assert err.type == AirModelAttributeError
