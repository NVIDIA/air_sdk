# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Union, List, Dict

from air_sdk.util import raise_if_invalid_response
from air_sdk.v2.endpoints import mixins
from air_sdk.v2.air_model import AirModel, BaseEndpointApi
from air_sdk.v2.endpoints.mixins import serialize_payload
from air_sdk.v2.utils import join_urls, validate_payload_types


@dataclass(eq=False)
class Worker(AirModel):
    id: str = field(repr=False)
    fqdn: str
    cpu_arch: str
    available: bool = field(repr=False)
    capabilities: str = field(repr=False)
    cpu: int = field(repr=False)
    contact: Union[str, List[str], Dict[str, str]] = field(repr=False)
    created: datetime = field(repr=False)
    fleet: str = field(repr=False)
    gpu: int = field(repr=False)
    ip_address: str = field(repr=False)
    memory: int = field(repr=False)
    modified: datetime = field(repr=False)
    port_range: str = field(repr=False)
    registered: bool = field(repr=False)
    storage: int = field(repr=False)
    tunnel_port: int = field(repr=False)
    vgpu: int = field(repr=False)

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return WorkerEndpointApi

    def heartbeat(self) -> None:
        """Keeps the worker alive with via a heartbeat to the manager."""
        heartbeat_url = join_urls(self.__api__.workers.url, 'heartbeat')
        response = self.__api__.client.get(heartbeat_url)
        raise_if_invalid_response(response, data_type=None)

    @validate_payload_types
    def update_inventory(
        self,
        airstrike_version: Optional[str] = None,
        architecture: Optional[str] = None,
        docker: Optional[str] = None,
        kernel: Optional[str] = None,
        libvirt: Optional[str] = None,
        operating_system: Optional[str] = None,
        proxy_image: Optional[str] = None,
        worker_version: Optional[str] = None,
    ) -> None:
        """Update the worker's inventory with the manager."""
        data = {
            'airstrike_version': airstrike_version,
            'architecture': architecture,
            'docker': docker,
            'kernel': kernel,
            'libvirt': libvirt,
            'operating_system': operating_system,
            'proxy_image': proxy_image,
            'worker_version': worker_version,
        }
        inventory_url = join_urls(self.__api__.workers.url, 'inventory')
        response = self.__api__.client.put(
            inventory_url,
            data=serialize_payload({key: value for (key, value) in data.items() if value is not None}),
        )
        raise_if_invalid_response(response, data_type=None)


class WorkerEndpointApi(
    mixins.ListApiMixin[Worker],
    mixins.GetApiMixin[Worker],
    BaseEndpointApi[Worker],
):
    API_PATH = 'workers'
    model = Worker
