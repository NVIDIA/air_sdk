# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from typing import Literal, Optional

from air_sdk.v2.endpoints import mixins
from air_sdk.v2.air_model import AirModel, PrimaryKey, BaseEndpointApi
from air_sdk.v2.endpoints.nodes import Node
from air_sdk.util import raise_if_invalid_response
from air_sdk.v2.utils import validate_payload_types


@dataclass(eq=False)
class NodeInstruction(AirModel):
    id: str = field(repr=False)
    node: Node = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    instruction: str
    state: str
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return NodeInstructionsEndpointApi

    @property
    def primary_key_field(self) -> str:
        return 'node'

    @property
    def __pk__(self) -> PrimaryKey:
        return getattr(self, self.primary_key_field).__pk__  # type: ignore


class NodeInstructionsEndpointApi(BaseEndpointApi[NodeInstruction]):
    API_PATH = 'simulations/nodes/{id}/instructions'  # Placeholder
    model = NodeInstruction

    @validate_payload_types
    def create(
        self,
        pk: PrimaryKey,
        executor: Literal['init', 'file', 'shell'],
        data: str,
        monitor: Optional[str] = None,
    ) -> NodeInstruction:
        params = {
            'executor': executor,
            'data': data,
        }
        if monitor:
            params['monitor'] = monitor

        detail_url = self.url.format(id=str(pk))
        response = self.__api__.client.post(detail_url, data=mixins.serialize_payload(params))
        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)
        return self.load_model(response.json())
