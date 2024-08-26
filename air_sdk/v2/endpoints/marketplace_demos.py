# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Union

from air_sdk.v2.endpoints import mixins, MarketplaceDemoTag, Account
from air_sdk.v2.endpoints.simulations import Simulation
from air_sdk.v2.air_model import AirModel, BaseEndpointApi, PrimaryKey, DataDict
from air_sdk.v2.utils import validate_payload_types


@dataclass(eq=False)
class MarketplaceDemo(AirModel):
    id: str
    name: str
    owner_email: str = field(repr=False)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    icon: Optional[str] = field(repr=False)
    liked_by_account: bool = field(repr=False)
    published: bool = field(repr=False)
    like_count: int = field(repr=False)
    snapshot: Simulation = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    repo: Optional[str] = field(repr=False)
    description: Optional[str] = field(repr=False)
    documentation: Optional[str] = field(repr=False)
    documentation_details: Optional[str] = field(metadata=AirModel.FIELD_LAZY, repr=False)
    tags: List[str] = field(default_factory=list, repr=False)

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return MarketplaceDemoEndpointApi

    @validate_payload_types
    def update(
        self,
        name: Optional[str] = None,
        snapshot: Optional[Union[Simulation, PrimaryKey]] = None,
        description: Optional[str] = None,
        documentation: Optional[str] = None,
        repo: Optional[str] = None,
        icon: Optional[str] = None,
        owner: Optional[Union[Account, PrimaryKey]] = None,
        tags: Optional[List[Union[MarketplaceDemoTag, str]]] = None,
        published: Optional[bool] = None,
    ) -> None:
        data = {
            'name': name,
            'snapshot': snapshot,
            'description': description,
            'documentation': documentation,
            'repo': repo,
            'icon': icon,
            'owner': owner,
            'tags': tags,
            'published': published,
        }
        data = {key: value for (key, value) in data.items() if value is not None}
        super().update(**data)

    @validate_payload_types
    def full_update(
        self,
        name: str,
        snapshot: Union[Simulation, PrimaryKey],
        description: Optional[str],
        documentation: Optional[str],
        repo: Optional[str],
        icon: Optional[str],
        owner: Optional[Union[Account, PrimaryKey]],
        tags: List[Union[MarketplaceDemoTag, str]],
        published: bool = False,
    ) -> None:
        data = {
            'name': name,
            'snapshot': snapshot,
            'description': description,
            'documentation': documentation,
            'repo': repo,
            'icon': icon,
            'owner': owner,
            'tags': tags,
            'published': published,
        }
        super().full_update(**data)


class MarketplaceDemoEndpointApi(
    mixins.ListApiMixin[MarketplaceDemo],
    mixins.CreateApiMixin[MarketplaceDemo],
    mixins.GetApiMixin[MarketplaceDemo],
    mixins.PutApiMixin[MarketplaceDemo],
    mixins.PatchApiMixin[MarketplaceDemo],
    mixins.DeleteApiMixin,
    BaseEndpointApi[MarketplaceDemo],
):
    API_PATH = 'marketplace-demos'

    model = MarketplaceDemo

    @validate_payload_types
    def create(
        self,
        name: str,
        snapshot: Union[Simulation, PrimaryKey],
        description: Optional[str] = None,
        documentation: Optional[str] = None,
        repo: Optional[str] = None,
        icon: Optional[str] = None,
        owner: Optional[Union[Account, PrimaryKey]] = None,
        tags: Optional[List[Union[MarketplaceDemoTag, str]]] = None,
        published: bool = False,
    ) -> MarketplaceDemo:
        payload: DataDict = {
            'snapshot': snapshot,
            'documentation': documentation,
            'repo': repo,
            'icon': icon,
            'name': name,
            'description': description,
            'published': published,
        }
        for key, value in (
            ('owner', owner),
            ('tags', tags),
        ):
            if value:
                payload[key] = value
        return super().create(**payload)
