# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from air_sdk.v2.endpoints import System


class TestSystemEndpointApi:
    def test_factory(self, run_api_not_implemented_test, system_factory):
        run_api_not_implemented_test(System, system_factory)
