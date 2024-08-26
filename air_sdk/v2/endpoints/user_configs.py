# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from typing import Optional, Union

from air_sdk.v2.endpoints import mixins
from air_sdk.v2.endpoints.accounts import Account
from air_sdk.v2.endpoints.organizations import Organization
from air_sdk.v2.air_model import AirModel, BaseEndpointApi, DataDict, PrimaryKey
from air_sdk.v2.endpoints.resource_budgets import ResourceBudget
from air_sdk.v2.utils import validate_payload_types


@dataclass(eq=False)
class UserConfig(AirModel):
    id: str = field(repr=False)
    name: str
    kind: str
    owner: Optional[Account] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    owner_budget: Optional[ResourceBudget] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    organization: Optional[Organization] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    organization_budget: Optional[ResourceBudget] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    content: Optional[str] = field(metadata=AirModel.FIELD_LAZY, repr=False)

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return UserConfigEndpointApi

    @validate_payload_types
    def update(self, name: Optional[str] = None, content: Optional[str] = None) -> None:
        """Update specific fields of the user config.."""
        data = {'name': name, 'content': content}
        data = {key: value for (key, value) in data.items() if value is not None}
        super().update(**data)

    @validate_payload_types
    def full_update(self, name: str, content: str) -> None:
        """Update all  fields of the cloud-init assignment."""
        super().full_update(
            name=name,
            content=content,
            owner=self.owner,
            owner_budget=self.owner_budget,
            kind=self.kind,
            organization=self.organization,
            organization_budget=self.organization_budget,
        )


class UserConfigEndpointApi(
    mixins.ListApiMixin[UserConfig],
    mixins.CreateApiMixin[UserConfig],
    mixins.GetApiMixin[UserConfig],
    mixins.PatchApiMixin[UserConfig],
    mixins.PutApiMixin[UserConfig],
    mixins.DeleteApiMixin,
    BaseEndpointApi[UserConfig],
):
    API_PATH = 'userconfigs'
    model = UserConfig

    @validate_payload_types
    def create(
        self,
        name: str,
        kind: str,
        content: str,
        organization: Optional[Union[Organization, PrimaryKey]] = None,
    ) -> UserConfig:
        payload: DataDict = {
            'name': name,
            'kind': kind,
            'content': content,
            'organization': organization,
        }
        return super().create(**payload)
