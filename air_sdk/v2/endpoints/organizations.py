# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field

from air_sdk.v2.endpoints import mixins
from air_sdk.v2.endpoints.resource_budgets import ResourceBudget
from air_sdk.v2.air_model import AirModel, BaseEndpointApi


@dataclass(eq=False)
class Organization(AirModel):
    id: str
    name: str
    member_count: int
    resource_budget: ResourceBudget = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return OrganizationEndpointApi


class OrganizationEndpointApi(
    mixins.ListApiMixin[Organization],
    mixins.GetApiMixin[Organization],
    BaseEndpointApi[Organization],
):
    API_PATH = 'organizations'
    model = Organization
