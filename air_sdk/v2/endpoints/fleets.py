# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from typing import Any, List, Optional, Union

from air_sdk.v2.air_model import AirModel, ApiNotImplementedMixin, BaseEndpointApi, PrimaryKey
from air_sdk.v2.endpoints import mixins
from air_sdk.v2.endpoints.organizations import Organization
from air_sdk.v2.utils import validate_payload_types


@dataclass(eq=False)
class FleetWorker(ApiNotImplementedMixin, AirModel):
    """Worker data returned in fleet responses"""

    id: str
    url: str
    cpu: int
    memory: int
    storage: int
    ip_address: str
    port_range: str
    region: str
    available: bool
    fqdn: str
    fleet: str
    contact: Union[List[str], str]
    capabilities: str
    cpu_arch: str

    @classmethod
    def get_model_api(cls):
        return FleetWorkerEndpointApi


class FleetWorkerEndpointApi(BaseEndpointApi[FleetWorker]):
    API_PATH = 'workers'  # placeholder
    model = FleetWorker

    def get(self, pk: PrimaryKey, **params: Any) -> FleetWorker:
        return self.load_model({'id': str(pk)})


@dataclass(eq=False)
class Fleet(AirModel):
    id: str
    name: str
    organization: Optional[Organization] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    prefix: str = field(repr=False)
    prefix_length: int = field(repr=False)
    gateway_ipv4: Optional[str] = field(repr=False)
    port_range: str = field(repr=False)
    container_ipv4_network: str = field(repr=False)
    container_prefix: int = field(repr=False)
    labels: List[str] = field(repr=False)
    public: bool = field(repr=False)
    workers: Optional[List[FleetWorker]] = field(repr=False)

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return FleetEndpointApi

    @validate_payload_types
    def update(
        self,
        name: Optional[str] = None,
        organization: Optional[Union[Organization, PrimaryKey]] = None,
        prefix: Optional[str] = None,
        prefix_length: Optional[int] = None,
        gateway_ipv4: Optional[str] = None,
        port_range: Optional[str] = None,
        container_ipv4_network: Optional[str] = None,
        container_prefix: Optional[int] = None,
        labels: Optional[List[str]] = None,
    ) -> None:
        data = {
            'name': name,
            'organization': organization,
            'prefix': prefix,
            'prefix_length': prefix_length,
            'gateway_ipv4': gateway_ipv4,
            'port_range': port_range,
            'container_ipv4_network': container_ipv4_network,
            'container_prefix': container_prefix,
            'labels': labels,
        }
        data = {key: value for (key, value) in data.items() if value is not None}
        super().update(**data)

    @validate_payload_types
    def full_update(
        self,
        name: str,
        organization: Union[Organization, PrimaryKey],
        prefix: Optional[str] = None,
        prefix_length: Optional[int] = None,
        gateway_ipv4: Optional[str] = None,
        port_range: Optional[str] = None,
        container_ipv4_network: Optional[str] = None,
        container_prefix: Optional[int] = None,
        labels: Optional[List[str]] = None,
    ) -> None:
        data = {
            'name': name,
            'organization': organization,
            'prefix': prefix,
            'prefix_length': prefix_length,
            'gateway_ipv4': gateway_ipv4,
            'port_range': port_range,
            'container_ipv4_network': container_ipv4_network,
            'container_prefix': container_prefix,
            'labels': labels,
        }
        data = {key: value for (key, value) in data.items() if value is not None}
        super().update(**data)


class FleetEndpointApi(
    mixins.ListApiMixin[Fleet],
    mixins.CreateApiMixin[Fleet],
    mixins.GetApiMixin[Fleet],
    mixins.PatchApiMixin[Fleet],
    mixins.PutApiMixin[Fleet],
    mixins.DeleteApiMixin,
    BaseEndpointApi[Fleet],
):
    API_PATH = 'fleet'
    model = Fleet

    @validate_payload_types
    def create(
        self,
        name: str,
        organization: Union[Organization, PrimaryKey],
        prefix: Optional[str] = None,
        prefix_length: Optional[int] = None,
        gateway_ipv4: Optional[str] = None,
        port_range: Optional[str] = None,
        container_ipv4_network: Optional[str] = None,
        container_prefix: Optional[int] = None,
        labels: Optional[List[str]] = None,
    ) -> Fleet:
        data = {
            'name': name,
            'organization': organization,
            'prefix': prefix,
            'prefix_length': prefix_length,
            'gateway_ipv4': gateway_ipv4,
            'port_range': port_range,
            'container_ipv4_network': container_ipv4_network,
            'container_prefix': container_prefix,
            'labels': labels,
        }
        data = {key: value for (key, value) in data.items() if value is not None}
        return super().create(**data)
