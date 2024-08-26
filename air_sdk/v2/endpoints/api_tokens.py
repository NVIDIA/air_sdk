# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from air_sdk.v2.endpoints import mixins
from air_sdk.v2.air_model import AirModel, BaseEndpointApi
from air_sdk.v2.utils import validate_payload_types


@dataclass(eq=False)
class ApiToken(AirModel):
    id: str = field(repr=False)
    name: str
    created: datetime = field(repr=False)
    expiry: Optional[datetime]

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return ApiTokenEndpointApi


class ApiTokenEndpointApi(
    mixins.ListApiMixin[ApiToken],
    mixins.CreateApiMixin[ApiToken],
    mixins.DeleteApiMixin,
    BaseEndpointApi[ApiToken],
):
    API_PATH = 'api-tokens'
    model = ApiToken

    @validate_payload_types
    def create(self, name: str, expiry: Optional[datetime] = None) -> ApiToken:
        return super().create(name=name, expiry=expiry)
