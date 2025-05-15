# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from typing import Literal, Optional, Union, TYPE_CHECKING, List, TypedDict, cast, Any, Dict

from air_sdk.util import raise_if_invalid_response
from air_sdk.v2.endpoints import mixins
from air_sdk.v2.endpoints.images import Image
from air_sdk.v2.endpoints.mixins import serialize_payload
from air_sdk.v2.endpoints.simulations import Simulation
from air_sdk.v2.endpoints.systems import System
from air_sdk.v2.endpoints.workers import Worker
from air_sdk.v2.air_model import AirModel, BaseEndpointApi, PrimaryKey, DataDict

from air_sdk.v2.utils import validate_payload_types, join_urls


if TYPE_CHECKING:
    from air_sdk.v2.endpoints.cloud_inits import CloudInit
    from air_sdk.v2.endpoints.node_instructions import NodeInstruction


class BulkUpdateSimNodeStateType(TypedDict):
    """Type hints for the payload of the `NodeEndpointApi.bulk_update_state` payload."""

    state: str
    ids: List[PrimaryKey]


class BulkUpdateSimNodeKeydiskType(TypedDict):
    """Type hints for the payload of the `NodeEndpointApi.bulk_update_keydisk` payload."""

    id: PrimaryKey
    agent_key: str


@dataclass(eq=False)
class Node(AirModel):
    id: str
    name: str
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    simulation: Simulation = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    os: Optional[Image] = field(metadata=AirModel.FIELD_FOREIGN_KEY)
    console_port: Optional[int] = field(repr=False)
    serial_port: Optional[int] = field(repr=False)
    state: str
    memory: int = field(repr=False)
    storage: int = field(repr=False)
    cpu: int = field(repr=False)
    version: int = field(repr=False)
    features: str = field(repr=False)
    simx_ipv4: Optional[str] = field(repr=False)  # We should remove this when plugin API is released
    worker: Optional[Worker] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    system: Optional[System] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    boot_group: Optional[int] = field(repr=False)
    console_url: Optional[str] = field(repr=False)
    console_username: Optional[str] = field(repr=False)
    console_password: Optional[str] = field(repr=False)
    metadata: Optional[str] = field(repr=False)
    pos_x: float = field(repr=False)
    pos_y: float = field(repr=False)

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return NodeEndpointApi

    @validate_payload_types
    def update(
        self,
        name: Optional[str] = None,
        state: Optional[str] = None,
        pos_x: Optional[float] = None,
        pos_y: Optional[float] = None,
        boot_group: Optional[int] = None,
        console_username: Optional[str] = None,
        console_password: Optional[str] = None,
        console_port: Optional[int] = None,
        serial_port: Optional[int] = None,
    ) -> None:
        data = {
            'name': name,
            'pos_x': pos_x,
            'pos_y': pos_y,
            'boot_group': boot_group,
            'console_username': console_username,
            'console_password': console_password,
            'console_port': console_port,
            'serial_port': serial_port,
            'state': state,
        }
        data = {key: value for (key, value) in data.items() if value is not None}
        super().update(**data)

    @validate_payload_types
    def full_update(
        self,
        name: str,
        state: str,
        pos_x: float,
        pos_y: float,
        boot_group: Optional[int],
        console_username: Optional[str],
        console_password: Optional[str],
        console_port: Optional[int],
        serial_port: Optional[int],
    ) -> None:
        super().update(
            name=name,
            state=state,
            pos_x=pos_x,
            pos_y=pos_y,
            boot_group=boot_group,
            console_username=console_username,
            console_password=console_password,
            console_port=console_port,
            serial_port=serial_port,
        )

    @validate_payload_types
    def set_agent_key(self, agent_key: Optional[str]) -> None:
        """Set the Air Agent key for the node.

        This is only used by worker clients when starting simulation nodes.
        """
        super().update(agent_key=agent_key)

    def create_node_instruction(
        self,
        executor: Literal['init', 'file', 'shell'],
        data: str,
        monitor: Optional[str] = None,
    ) -> NodeInstruction:
        """Add a node instruction to the node."""
        node_instruction: NodeInstruction = self.__api__.node_instructions.create(
            pk=self.__pk__,
            executor=executor,
            data=data,
            monitor=monitor,
        )
        return node_instruction

    @property
    def cloud_init(self) -> CloudInit:
        cloud_int: CloudInit = self.__api__.cloud_inits.get(self.__pk__)
        return cloud_int

    def __control(self, action: str) -> None:
        """Internal method to handle control commands."""
        payload = {'action': action}
        response = self.__api__.client.post(join_urls(self.detail_url, 'control'), json=payload)
        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED, data_type=list)

    def rebuild(self) -> None:
        """
        Rebuild the `SimulationNode` back to it's initial state. **All existing data will be lost!**
        """
        self.__control(action='rebuild')

    def reset(self) -> None:
        """Reset the `SimulationNode`"""
        self.__control(action='reset')


class NodeEndpointApi(
    mixins.ListApiMixin[Node],
    mixins.CreateApiMixin[Node],
    mixins.GetApiMixin[Node],
    mixins.PatchApiMixin[Node],
    mixins.DeleteApiMixin,
    BaseEndpointApi[Node],
):
    API_PATH = 'simulations/nodes/'
    model = Node

    @validate_payload_types
    def create(
        self,
        simulation: Union[Simulation, PrimaryKey],
        name: str,
        pos_x: float = 0.0,
        pos_y: float = 0.0,
        boot_group: Optional[int] = 50,
        features: str = '{}',
        metadata: str = '{}',
        os: Optional[Union[Image, PrimaryKey]] = None,
        system: Optional[Union[System, PrimaryKey]] = None,
        memory: Optional[int] = None,
        cpu: Optional[int] = None,
        storage: Optional[int] = None,
        console_username: Optional[str] = None,
        console_password: Optional[str] = None,
    ) -> Node:
        payload: DataDict = {
            'simulation': simulation,
            'name': name,
            'os': os,
            'boot_group': boot_group,
            'features': features,
            'pos_x': pos_x,
            'pos_y': pos_y,
            'console_username': console_username,
            'console_password': console_password,
            'metadata': metadata,
        }
        for key, value in (
            ('system', system),
            ('storage', storage),
            ('memory', memory),
            ('cpu', cpu),
        ):
            if value is not None:
                payload[key] = value
        return super().create(**payload)

    @validate_payload_types
    def bulk_update_state(self, data: List[BulkUpdateSimNodeStateType]) -> None:
        """Method used by worker clients to perform state updates of nodes in bulk."""
        response = self.__api__.client.patch(
            join_urls(self.url, 'bulk-update-state'),
            data=serialize_payload(cast(List[Dict[str, Any]], data)),
        )
        raise_if_invalid_response(response, status_code=HTTPStatus.OK, data_type=None)

    @validate_payload_types
    def bulk_update_keydisk(self, data: List[BulkUpdateSimNodeKeydiskType]) -> None:
        """Method used by worker clients to perform keydisk updates of nodes in bulk."""
        response = self.__api__.client.patch(
            join_urls(self.url, 'bulk-update-keydisk'),
            data=serialize_payload(cast(List[Dict[str, Any]], data)),
        )
        raise_if_invalid_response(response, status_code=HTTPStatus.OK, data_type=None)
