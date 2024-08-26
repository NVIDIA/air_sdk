# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

from air_sdk.v2.endpoints import mixins
from air_sdk.v2.endpoints import Account
from air_sdk.v2.endpoints.organizations import Organization
from air_sdk.v2.air_model import AirModel, BaseEndpointApi


@dataclass(eq=False)
class Image(AirModel):
    id: str = field(repr=False)
    agent_enabled: bool = field(repr=False)
    archived: bool = field(repr=False)
    bios: Optional['Image'] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    bus: str = field(repr=False)
    console_support: Dict[str, Any] = field(repr=False)
    cpu_arch: str = field(repr=False)
    created: datetime = field(repr=False)
    default_username: Optional[str] = field(repr=False)
    default_password: Optional[str] = field(repr=False)
    features: Dict[str, Any] = field(repr=False)
    modified: Optional[datetime] = field(repr=False)
    mountpoint: Optional[str] = field(repr=False)
    minimum_resources: Dict[str, int] = field(repr=False)
    name: Optional[str]
    notes: Optional[str] = field(repr=False)
    organization: Optional[Organization] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    published: Optional[bool] = field(repr=False)
    provider: Optional[str] = field(repr=False)
    release_notes: Optional[str] = field(repr=False)
    simx: Optional[str] = field(repr=False)
    size: int = field(repr=False)
    upload_status: str = field(repr=False)
    uploader: Optional[Account] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    user_manual: Optional[str] = field(repr=False)
    version: str
    can_edit: bool = field(repr=False)
    organization_name: Optional[str]
    uploader_username: Optional[str] = field(repr=False)

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return ImageEndpointApi


class ImageEndpointApi(mixins.ListApiMixin[Image], mixins.GetApiMixin[Image], BaseEndpointApi[Image]):
    API_PATH = 'images'
    model = Image
