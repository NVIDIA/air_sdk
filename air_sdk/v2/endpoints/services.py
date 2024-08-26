# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT


from dataclasses import field, dataclass
from datetime import datetime
from typing import Optional, Union

from air_sdk.v2.endpoints import mixins
from air_sdk.v2.endpoints.interfaces import Interface
from air_sdk.v2.endpoints.simulations import Simulation
from air_sdk.v2.air_model import AirModel, BaseEndpointApi, PrimaryKey
from air_sdk.v2.utils import validate_payload_types


@dataclass(eq=False)
class Service(AirModel):
    id: str
    name: str
    created: datetime
    modified: datetime
    dest_port: int
    src_port: int
    service_type: str
    interface: Interface = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    simulation: Simulation = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    host: Optional[str]

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return ServiceEndpointApi


class ServiceEndpointApi(
    mixins.ListApiMixin[Service],
    mixins.CreateApiMixin[Service],
    mixins.DeleteApiMixin,
    BaseEndpointApi[Service],
):
    API_PATH = 'simulations/nodes/interfaces/services/'
    model = Service

    @validate_payload_types
    def create(
        self, name: str, dest_port: int, interface: Union[Interface, PrimaryKey], service_type: str = 'ssh'
    ) -> Service:
        return super().create(
            name=name,
            dest_port=dest_port,
            interface=interface,
            service_type=service_type,
        )
