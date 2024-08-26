# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from air_sdk.v2.endpoints import ResourceBudget


class TestResourceBudgetEndpointApi:
    def test_factory(self, run_api_not_implemented_test, resource_budget_factory):
        run_api_not_implemented_test(ResourceBudget, resource_budget_factory)
