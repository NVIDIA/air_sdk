# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from air_sdk.v2.endpoints import mixins
from air_sdk.v2.air_model import AirModel, BaseEndpointApi
from air_sdk.v2.utils import validate_payload_types


@dataclass(eq=False)
class Announcement(AirModel):
    id: str = field(repr=False)
    severity: str
    created: datetime
    modified: datetime = field(repr=False)
    message: Optional[str] = field(repr=False)

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return AnnouncementEndpointApi


class AnnouncementEndpointApi(
    mixins.ListApiMixin[Announcement],
    mixins.CreateApiMixin[Announcement],
    mixins.DeleteApiMixin,
    BaseEndpointApi[Announcement],
):
    API_PATH = 'announcements'
    model = Announcement

    @validate_payload_types
    def create(self, severity: str, message: str) -> Announcement:
        return super().create(severity=severity, message=message)
