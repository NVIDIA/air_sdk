# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, List, Any
from air_sdk.v2.endpoints import mixins
from air_sdk.v2.endpoints.resource_budgets import ResourceBudget
from air_sdk.v2.air_model import AirModel, BaseEndpointApi, PrimaryKey
from air_sdk.v2.utils import validate_payload_types


@dataclass(eq=False)
class Organization(AirModel):
    id: str
    name: str
    member_count: int
    resource_budget: ResourceBudget = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)

    def list_members(self) -> Iterator[OrganizationMember]:
        """Returns an iterator of organization members."""
        members_api = OrganizationMembersEndpointApi(self.__api__)
        return members_api.list_organization_members(self.id)

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


@dataclass(eq=False)
class OrganizationMember(AirModel):
    id: str
    username: str
    roles: List[str]
    resource_budget: ResourceBudget = field(metadata=AirModel.FIELD_FOREIGN_KEY)

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return OrganizationMembersEndpointApi


class OrganizationMembersEndpointApi(
    mixins.ListApiMixin[OrganizationMember],
    BaseEndpointApi[OrganizationMember],
):
    API_PATH = 'organization/{id}/members'
    model = OrganizationMember

    @validate_payload_types
    def list_organization_members(
        self, organization: PrimaryKey, **params: Any
    ) -> Iterator[OrganizationMember]:
        """Return an iterator of organization member instances for a specific organization."""
        self.url = self.url.format(id=organization)
        return super().list(**params)
