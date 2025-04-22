# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional, Union

from air_sdk.v2.endpoints import mixins
from air_sdk.v2.endpoints.nodes import Node
from air_sdk.v2.endpoints.interfaces import Interface
from air_sdk.v2.air_model import AirModel, ApiNotImplementedMixin, BaseEndpointApi, PrimaryKey
from air_sdk.v2.utils import validate_payload_types


@dataclass(eq=False)
class BreakoutInterface(ApiNotImplementedMixin, AirModel):
    """
    Interface created from a breakout operation.
    Represents a simplified interface model returned in breakout responses.
    """

    id: str = field(repr=False)
    name: str

    @classmethod
    def get_model_api(cls):
        return BreakoutInterfaceEndpointApi


class BreakoutInterfaceEndpointApi(BaseEndpointApi[BreakoutInterface]):
    API_PATH = 'interfaces'
    model = BreakoutInterface

    def get(self, pk: PrimaryKey, **params: Any) -> BreakoutInterface:
        return self.load_model({'id': str(pk)})


@dataclass(eq=False)
class Breakout(AirModel):
    id: str = field(repr=False)
    node: Node = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    name: str
    mac_address: Optional[str] = field(repr=False)
    split_count: int
    simulation_interfaces: List[BreakoutInterface] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    created: Optional[datetime] = field(repr=False)

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return BreakoutEndpointApi


class BreakoutEndpointApi(
    mixins.ListApiMixin[Breakout],
    mixins.CreateApiMixin[Breakout],
    mixins.GetApiMixin[Breakout],
    mixins.DeleteApiMixin,
    BaseEndpointApi[Breakout],
):
    API_PATH = 'simulations/nodes/interfaces/breakouts/'
    model = Breakout

    @validate_payload_types
    def create(self, interface: Union[Interface, PrimaryKey], split_count: int) -> Breakout:
        """
        Create a new breakout configuration.

        Args:
            interface: The interface to break out
            split_count: Number of splits to create (minimum value: 2)

        Returns:
            Breakout: The created breakout configuration
        """
        return super().create(interface=interface, split_count=split_count)
