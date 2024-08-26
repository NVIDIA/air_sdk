# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Union

from air_sdk.v2.endpoints import mixins
from air_sdk.v2.endpoints.organizations import Organization
from air_sdk.v2.endpoints.workers import Worker
from air_sdk.v2.air_model import AirModel, BaseEndpointApi, DataDict, PrimaryKey
from air_sdk.v2.utils import validate_payload_types


@dataclass(eq=False)
class Simulation(AirModel):
    id: str
    title: str
    state: str
    sleep: bool = field(repr=False)
    owner: str = field(repr=False)
    cloned: bool = field(repr=False)
    expires: bool = field(repr=False)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    sleep_at: datetime = field(repr=False)
    expires_at: datetime = field(repr=False)
    organization: Optional[Organization] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    preferred_worker: Optional[Worker] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    documentation: Optional[str]
    write_ok: Optional[bool]
    metadata: Optional[str]

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return SimulationEndpointApi

    @validate_payload_types
    def update(
        self,
        documentation: Optional[str] = None,
        expires: Optional[bool] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[str] = None,
        preferred_worker: Optional[Union[Worker, PrimaryKey]] = None,
        sleep: Optional[bool] = None,
        sleep_at: Optional[datetime] = None,
        title: Optional[str] = None,
    ) -> None:
        data = {
            'documentation': documentation,
            'expires': expires,
            'expires_at': expires_at,
            'metadata': metadata,
            'preferred_worker': preferred_worker,
            'sleep': sleep,
            'sleep_at': sleep_at,
            'title': title,
        }
        data = {key: value for (key, value) in data.items() if value is not None}
        super().update(**data)

    @validate_payload_types
    def full_update(
        self,
        documentation: Optional[str],
        expires: bool,
        expires_at: datetime,
        metadata: Optional[str],
        preferred_worker: Optional[Union[Worker, PrimaryKey]],
        sleep: bool,
        sleep_at: datetime,
        title: str,
    ) -> None:
        super().update(
            documentation=documentation,
            expires=expires,
            expires_at=expires_at,
            metadata=metadata,
            preferred_worker=preferred_worker,
            sleep=sleep,
            sleep_at=sleep_at,
            title=title,
        )


class SimulationEndpointApi(
    mixins.ListApiMixin[Simulation],
    mixins.CreateApiMixin[Simulation],
    mixins.GetApiMixin[Simulation],
    mixins.PatchApiMixin[Simulation],
    mixins.DeleteApiMixin,
    BaseEndpointApi[Simulation],
):
    API_PATH = 'simulations'
    model = Simulation

    @validate_payload_types
    def create(
        self,
        title: str,
        documentation: Optional[str] = None,
        expires: Optional[bool] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[str] = None,
        organization: Optional[Union[Organization, PrimaryKey]] = None,
        owner: Optional[str] = None,
        preferred_worker: Optional[Union[Worker, PrimaryKey]] = None,
        sleep: Optional[bool] = None,
        sleep_at: Optional[datetime] = None,
    ) -> Simulation:
        payload: DataDict = {'title': title}
        for key, value in (
            ('documentation', documentation),
            ('expires', expires),
            ('expires_at', expires_at),
            ('metadata', metadata),
            ('organization', organization),
            ('owner', owner),
            ('preferred_worker', preferred_worker),
            ('sleep', sleep),
            ('sleep_at', sleep_at),
        ):
            if value is not None:  # Don't include optional None fields in payload.
                payload[key] = value
        return super().create(**payload)
