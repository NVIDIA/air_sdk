# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from air_sdk.v2.endpoints import mixins
from air_sdk.v2.endpoints.simulations import Simulation
from air_sdk.v2.endpoints.workers import Worker
from air_sdk.v2.air_model import AirModel, BaseEndpointApi
from air_sdk.v2.utils import validate_payload_types


@dataclass(eq=False)
class Job(AirModel):
    id: str
    category: str
    state: str
    created: datetime = field(repr=False)
    last_updated: datetime = field(repr=False)
    notes: Optional[str] = field(repr=False)
    data: Optional[str] = field(repr=False)
    simulation: Optional[Simulation] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    worker: Optional[Worker] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return JobEndpointApi

    @validate_payload_types
    def update(self, state: str) -> None:
        super().update(state=state)


class JobEndpointApi(
    mixins.ListApiMixin[Job],
    mixins.GetApiMixin[Job],
    mixins.PatchApiMixin[Job],
    BaseEndpointApi[Job],
):
    API_PATH = 'jobs'
    model = Job
