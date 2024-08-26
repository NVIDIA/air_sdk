# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from air_sdk.v2.endpoints import Account


class TestAccountEndpointApi:
    def test_factory(self, run_api_not_implemented_test, account_factory):
        run_api_not_implemented_test(Account, account_factory)
