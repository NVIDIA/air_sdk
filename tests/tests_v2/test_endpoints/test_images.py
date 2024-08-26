# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT


class TestImageEndpointApi:
    def test_list(self, api, run_list_test, image_factory):
        run_list_test(api.images, image_factory)

    def test_refresh(self, api, run_refresh_test, image_factory):
        run_refresh_test(api.images, image_factory)
