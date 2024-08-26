# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass

from air_sdk.v2.endpoints import mixins
from air_sdk.v2.air_model import AirModel, BaseEndpointApi


@dataclass(eq=False)
class MarketplaceDemoTag(AirModel):
    name: str

    @property
    def primary_key_field(self) -> str:
        return 'name'

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return MarketplaceDemoTagsEndpointApi


class MarketplaceDemoTagsEndpointApi(
    mixins.ListApiMixin[MarketplaceDemoTag], BaseEndpointApi[MarketplaceDemoTag]
):
    API_PATH = 'marketplace-demo-tags'

    model = MarketplaceDemoTag
