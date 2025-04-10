# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any, Iterable, Optional, TypedDict, Union

from air_sdk.util import raise_if_invalid_response
from air_sdk.v2.air_model import AirModel, BaseEndpointApi, PrimaryKey
from air_sdk.v2.endpoints.mixins import serialize_payload
from air_sdk.v2.endpoints.nodes import Node
from air_sdk.v2.endpoints.user_configs import UserConfig
from air_sdk.v2.utils import join_urls, validate_payload_types


class CloudInitBulkAssignment(TypedDict, total=False):
    user_data: Optional[Union[UserConfig, PrimaryKey]]
    meta_data: Optional[Union[UserConfig, PrimaryKey]]
    simulation_node: Union[Node, PrimaryKey]


@dataclass(eq=False)
class CloudInit(AirModel):
    simulation_node: Node = field(metadata=AirModel.FIELD_FOREIGN_KEY)
    user_data: Optional[UserConfig] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    meta_data: Optional[UserConfig] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    user_data_name: Optional[str]
    meta_data_name: Optional[str]

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return CloudInitEndpointApi

    @property
    def primary_key_field(self) -> str:
        return 'simulation_node'

    @property
    def __pk__(self) -> PrimaryKey:
        return getattr(self, self.primary_key_field).__pk__  # type: ignore

    @validate_payload_types
    def full_update(
        self,
        user_data: Optional[Union[UserConfig, PrimaryKey]],
        meta_data: Optional[Union[UserConfig, PrimaryKey]],
    ) -> None:
        """Update all fields of the cloud-init assignment."""
        super().update(user_data=user_data, meta_data=meta_data)


class CloudInitEndpointApi(BaseEndpointApi[CloudInit]):
    API_PATH = 'simulations/nodes/{id}/cloud-init'  # Placeholder
    BULK_API_PATH = 'simulations/nodes/cloud-init/bulk-assign'
    model = CloudInit

    def get(self, pk: PrimaryKey, **params: Any) -> CloudInit:
        detail_url = self.url.format(id=str(pk))
        response = self.__api__.client.get(detail_url, params=params)
        raise_if_invalid_response(response)
        return self.load_model(response.json())

    def patch(self, pk: PrimaryKey, **kwargs: Any) -> CloudInit:
        detail_url = self.url.format(id=str(pk))
        response = self.__api__.client.patch(detail_url, data=serialize_payload(kwargs))
        raise_if_invalid_response(response)
        return self.load_model(response.json())

    @validate_payload_types
    def bulk_assign(self, assignments: Iterable[CloudInitBulkAssignment]) -> None:
        response = self.__api__.client.patch(
            join_urls(self.__api__.client.base_url, self.BULK_API_PATH),
            data=serialize_payload([dict(assignment) for assignment in assignments]),
        )
        raise_if_invalid_response(response, status_code=HTTPStatus.NO_CONTENT, data_type=None)
