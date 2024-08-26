# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

import pytest
import faker

faker.Faker.seed(0)
fake = faker.Faker()


class TestUserConfigEndpointApi:
    def test_list(self, api, run_list_test, user_config_factory):
        run_list_test(api.user_configs, user_config_factory)

    def test_refresh(self, api, run_refresh_test, user_config_factory):
        run_refresh_test(api.user_configs, user_config_factory)

    def test_delete(self, api, run_delete_test, user_config_factory):
        run_delete_test(api.user_configs, user_config_factory)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({}, False),
            ({'name': None, 'kind': None, 'content': None}, False),
            ({'name': fake.slug(), 'kind': fake.slug(), 'content': fake.binary()}, False),
            ({'name': fake.slug(), 'kind': fake.slug(), 'content': fake.slug()}, True),
            (
                {'name': fake.slug(), 'kind': fake.slug(), 'content': fake.slug(), 'owner': fake.pyint()},
                False,
            ),
            (
                {
                    'name': fake.slug(),
                    'kind': fake.slug(),
                    'content': fake.slug(),
                },
                True,
            ),
        ),
    )
    def test_create(self, api, user_config_factory, run_create_test_case, payload, is_valid):
        """This tests that the data provided is properly validated and used."""
        run_create_test_case(api.user_configs, user_config_factory, payload, is_valid)

    def test_update(
        self,
        api,
        run_update_patch_test,
        user_config_factory,
    ):
        cases = (
            ({}, True),
            ({'name': None}, True),
            ({'name': fake.slug()}, True),
            ({'name': fake.pybool()}, False),
            ({'content': None}, True),
            ({'content': fake.text()}, True),
            ({'content': fake.pyint()}, False),
            ({'name': fake.slug(), 'content': fake.slug()}, True),
            ({'fake_field': None}, False),
        )
        for payload, is_valid in cases:
            run_update_patch_test(api.user_configs, user_config_factory, payload, is_valid)

    def test_full_update(
        self,
        api,
        run_full_update_put_test,
        user_config_factory,
        organization_factory,
    ):
        cases = (
            ({}, False),
            ({'name': None, 'content': None}, False),
            ({'name': None, 'content': fake.text()}, False),
            ({'name': fake.slug(), 'content': None}, False),
            ({'name': fake.slug(), 'content': fake.text()}, True),
            ({'name': fake.slug(), 'content': fake.text(), 'unexpected_field': fake.slug()}, False),
        )
        for payload, is_valid in cases:
            run_full_update_put_test(api.user_configs, user_config_factory, payload, is_valid)


class TestUserConfigModelRelations:
    def test_owner_access(self, api, user_config_factory):
        user_config = user_config_factory(api)
        owner = user_config.owner
        assert owner.__fk_resolved__ is False
        assert owner.id is not None
        assert owner.__fk_resolved__ is True
        with pytest.raises(NotImplementedError):
            owner.refresh()

    def test_owner_budget_access(self, api, user_config_factory):
        user_config = user_config_factory(api)
        owner_budget = user_config.owner_budget
        assert owner_budget.__fk_resolved__ is False
        assert owner_budget.id is not None
        assert owner_budget.__fk_resolved__ is True
        with pytest.raises(NotImplementedError):
            owner_budget.refresh()

    def test_organization_budget_access(self, api, user_config_factory):
        user_config = user_config_factory(api)
        organization_budget = user_config.organization_budget
        assert organization_budget.__fk_resolved__ is False
        assert organization_budget.id is not None
        assert organization_budget.__fk_resolved__ is True
        with pytest.raises(NotImplementedError):
            organization_budget.refresh()
