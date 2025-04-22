# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Literal, Optional, List, Dict, Union, Any, Iterator, Type, TYPE_CHECKING

from air_sdk.util import raise_if_invalid_response

from air_sdk.v2.endpoints import mixins
from air_sdk.v2.endpoints.mixins import serialize_payload

from air_sdk.v2.endpoints.nodes import Node
from air_sdk.v2.endpoints.simulations import Simulation
from air_sdk.v2.air_model import AirModel, BaseEndpointApi, PrimaryKey, DataDict, BaseModel

from air_sdk.v2.utils import validate_payload_types, join_urls

if TYPE_CHECKING:
    from air_sdk.v2 import AirApi
    from air_sdk.v2.endpoints.breakouts import Breakout


@dataclass(eq=False)
class Interface(AirModel):
    id: str
    name: str
    link_up: bool
    internal_ipv4: Optional[str]
    full_ipv6: Optional[str]
    prefix_ipv6: Optional[str]
    interface_type: Optional[str]
    port_number: int
    preserve_mac: bool
    outbound: bool
    mac_address: Optional[str]
    node: Node = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    simulation: Simulation = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    link: Optional[Link] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)

    def __post_init__(self, _api: AirApi) -> None:
        super().__post_init__(_api)
        if self.link is not None:
            self.link.__simulation_pk__ = self.simulation.__pk__  # type: ignore[attr-defined]

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return InterfaceEndpointApi

    @validate_payload_types
    def update(
        self,
        name: Optional[str] = None,
        port_number: Optional[int] = None,
        outbound: Optional[bool] = None,
        preserve_mac: Optional[bool] = None,
        link_up: Optional[bool] = None,
        link: Optional[Union[Link, PrimaryKey]] = None,
    ) -> None:
        data = {
            'name': name,
            'link_up': link_up,
            'port_number': port_number,
            'outbound': outbound,
            'preserve_mac': preserve_mac,
            'link': link,
        }
        data = {key: value for (key, value) in data.items() if value is not None}
        super().update(**data)

    @validate_payload_types
    def full_update(
        self,
        name: str,
        port_number: int,
        outbound: bool,
        preserve_mac: bool,
        link_up: bool,
        link: Optional[Union[Link, PrimaryKey]],
    ) -> None:
        data = {
            'name': name,
            'link_up': link_up,
            'port_number': port_number,
            'outbound': outbound,
            'preserve_mac': preserve_mac,
            'link': link,
        }
        super().update(**data)

    def breakout(self, split_count: int) -> Breakout:
        """
        Create a breakout configuration for this interface.

        Args:
            split_count: Number of splits to create (minimum value: 2)

        Returns:
            Breakout: The created breakout configuration

        """
        payload: DataDict = {
            'interface': self.__pk__,
            'split_count': split_count,
        }
        response = self.__api__.client.post(self.__api__.breakouts.url, data=serialize_payload(payload))
        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)
        return self.__api__.breakouts.load_model(response.json())


class InterfaceEndpointApi(
    mixins.ListApiMixin[Interface],
    mixins.CreateApiMixin[Interface],
    mixins.GetApiMixin[Interface],
    mixins.PatchApiMixin[Interface],
    mixins.DeleteApiMixin,
    BaseEndpointApi[Interface],
):
    API_PATH = 'simulations/nodes/interfaces/'
    model = Interface

    @validate_payload_types
    def create(
        self,
        name: str,
        node: Union[Node, PrimaryKey],
        interface_type: Union[str, Literal['DATA_PLANE_INTF']] = 'DATA_PLANE_INTF',
        link_up: bool = False,
        port_number: int = 0,
        outbound: bool = False,
        preserve_mac: bool = False,
        mac_address: Optional[str] = None,
        internal_ipv4: Optional[str] = None,
        full_ipv6: Optional[str] = None,
        prefix_ipv6: Optional[str] = None,
        link: Optional[Union[Link, PrimaryKey]] = None,
    ) -> Interface:
        return super().create(
            name=name,
            node=node,
            interface_type=interface_type,
            link_up=link_up,
            port_number=port_number,
            outbound=outbound,
            preserve_mac=preserve_mac,
            internal_ipv4=internal_ipv4,
            full_ipv6=full_ipv6,
            prefix_ipv6=prefix_ipv6,
            mac_address=mac_address,
            link=link,
        )


"""
Link and Interface share a module to prevent circular import issues.
"""

LinkDataList = List[Dict[str, List[Union[PrimaryKey, Interface]]]]


@dataclass(eq=False)
class Link(AirModel):
    id: str
    simulation_interfaces: List[Interface] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)

    def __refresh__(self, refreshed_obj: Optional[BaseModel] = None) -> None:
        link_api = self.get_model_api()(self.__api__)
        refreshed_obj = next(link_api.list(simulation=self.__simulation_pk__, ids=str(self.__pk__)))
        super().__refresh__(refreshed_obj)

    @classmethod
    def get_model_api(cls) -> Type[LinkEndpointApi]:
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return LinkEndpointApi


class LinkEndpointApi(mixins.ListApiMixin[Link], mixins.GetApiMixin[Link], BaseEndpointApi[Link]):
    API_PATH = 'simulations/nodes/interfaces/links/'
    model = Link

    def list(self, simulation: Union[Simulation, PrimaryKey], **params: Any) -> Iterator[Link]:  # type: ignore[override]
        if simulation is None:
            raise TypeError('simulation may not be `None`.')
        return super().list(simulation=simulation, **params)

    @validate_payload_types
    def get(self, pk: PrimaryKey, simulation: Union[Simulation, PrimaryKey]) -> Link:  # type: ignore[override]
        sim_id = getattr(simulation, '__pk__', simulation)
        return super().get(pk=pk, simulation=sim_id)

    @validate_payload_types
    def bulk_create(self, simulation: Union[Simulation, PrimaryKey], links: LinkDataList) -> List[Link]:
        payload = {'simulation': simulation, 'links': links}
        if len(links) == 0:
            raise ValueError('links must be a non-empty list of dictionaries.')
        for i, link in enumerate(links):
            # Validate the payload format and make content json serializable.
            sim_iface_key = 'simulation_interfaces'
            if set(link.keys()) != {sim_iface_key}:
                raise ValueError(
                    'Expected link to have format {"simulation_interfaces": [interface_1, interface_2]} '
                    f'but got {link}'
                )

        response = self.__api__.client.post(
            join_urls(self.url, 'bulk-create'), data=serialize_payload(payload)
        )
        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)
        response_data: DataDict = response.json()
        link_data_list = response_data['links']
        return [self.load_model(link_data) for link_data in link_data_list]

    @validate_payload_types
    def bulk_delete(
        self, simulation: Union[Simulation, PrimaryKey], links: Optional[List[Union[Link, PrimaryKey]]] = None
    ) -> Dict[str, int]:
        if not simulation:
            raise ValueError('`simulation` must be specified')
        if isinstance(links, list) and len(links) == 0:
            raise ValueError('If `links` is provided it must be a non-empty list.')
        params = json.loads(serialize_payload({'simulation': simulation, 'links': links}))
        link_id_list = params.pop('links')
        if isinstance(link_id_list, list):
            params['ids'] = ','.join(link_id_list)
        response = self.__api__.client.delete(join_urls(self.url, 'bulk-delete'), params=params)
        raise_if_invalid_response(response, status_code=HTTPStatus.OK)
        links_deleted: int = response.json()['links_deleted']
        return {'links_deleted': links_deleted}
