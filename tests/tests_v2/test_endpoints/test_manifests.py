# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

import faker
import pytest

faker.Faker.seed(0)
fake = faker.Faker()


class TestManifestEndpointApi:
    def test_list(self, api, run_list_test, manifest_factory):
        run_list_test(api.manifests, manifest_factory)

    def test_refresh(self, api, run_refresh_test, manifest_factory):
        run_refresh_test(api.manifests, manifest_factory)

    def test_delete(self, api, run_delete_test, manifest_factory):
        run_delete_test(api.manifests, manifest_factory)


class TestManifestModelRelations:
    def test_owner_access(self, api, manifest_factory):
        manifest = manifest_factory(api)
        owner = manifest.owner
        assert owner.__fk_resolved__ is False
        assert owner.id is not None
        assert owner.__fk_resolved__ is True
        with pytest.raises(NotImplementedError):
            owner.refresh()
