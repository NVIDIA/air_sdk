# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from io import TextIOBase, TextIOWrapper
from pathlib import Path
from typing import Callable, Dict, Literal, Optional, TypedDict, Union, cast

from air_sdk.util import raise_if_invalid_response
from air_sdk.v2.air_model import AirModel, BaseEndpointApi, DataDict, PrimaryKey
from air_sdk.v2.endpoints import mixins
from air_sdk.v2.endpoints.organizations import Organization
from air_sdk.v2.endpoints.workers import Worker
from air_sdk.v2.utils import join_urls, validate_payload_types

TopologyFormatContent = Union[Dict[str, object]]
TopologyFormatType = Literal['JSON']
SimulationImportPayloadContent = Union[str, TopologyFormatContent, Path, TextIOWrapper]


class SimulationDuplicatePayload(TypedDict, total=False):
    start: bool


class SimulationDuplicateResponseSimulationField(TypedDict):
    id: str


class SimulationDuplicateResponse(TypedDict):
    simulation: SimulationDuplicateResponseSimulationField


class SimulationImportResponse(TypedDict):
    id: str
    title: str
    organization: Optional[str]
    organization_name: Optional[str]


class TopologyFormat(TypedDict, total=False):
    title: str
    format: TopologyFormatType
    organization: Union[Organization, PrimaryKey]  # NotRequired
    content: TopologyFormatContent


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

    @validate_payload_types
    def export(
        self,
        format: TopologyFormatType,
        image_ids: bool = False,
    ) -> TopologyFormatContent:
        """
        Exports this simulation into a desired topology format.

        :Arguments:
        - `format`: desired output format (currently supported format is `JSON`)
        - `image_ids`: whether to return image IDs instead of names
        """
        return self.__api__.simulations.export(self, format, image_ids)

    def load(self) -> None:
        """Starts the simulation. Previously stored simulation will get loaded from its last state."""
        response = self.__api__.client.post(join_urls(self.detail_url, 'load'))
        raise_if_invalid_response(response, status_code=HTTPStatus.OK)
        self.refresh()

    def start(self) -> None:
        """Starts the simulation. Previously stored simulation will get loaded from its last state."""
        self.load()

    def store(self) -> None:
        """Stops the simulation and stores its state."""
        response = self.__api__.client.post(join_urls(self.detail_url, 'store'))
        raise_if_invalid_response(response, status_code=HTTPStatus.OK)
        self.refresh()

    def stop(self) -> None:
        """Stops the simulation and stores its state."""
        self.store()

    def rebuild(self) -> None:
        """Rebuilds all nodes of the simulation. Current memory and disk changes of all nodes will be lost."""
        response = self.__api__.client.post(join_urls(self.detail_url, 'rebuild'))
        raise_if_invalid_response(response, status_code=HTTPStatus.OK)
        self.refresh()

    def extend(self) -> datetime:
        """Postpones the simulation's sleep date. Returns the new sleep date."""
        response = self.__api__.client.post(join_urls(self.detail_url, 'extend'))
        raise_if_invalid_response(response, status_code=HTTPStatus.OK)
        self.refresh()

        return self.sleep_at

    @validate_payload_types
    def duplicate(
        self,
        start: Optional[bool] = None,
    ) -> Simulation:
        """
        Duplicates the simulation and returns the `Simulation` instance of the clone.

        :Arguments:
        - `start`: Whether the cloned simulation should get started automatically. Set to `None` in order to rely on the default value of the backend.
        """
        payload = SimulationDuplicatePayload()
        if start is not None:
            payload['start'] = start

        # Perform duplication request
        response = self.__api__.client.post(join_urls(self.detail_url, 'duplicate'), json=payload)
        raise_if_invalid_response(response, status_code=HTTPStatus.OK)
        self.refresh()  # Refresh potentially new state of the original simulation

        # Fetch the clone
        duplication_response: SimulationDuplicateResponse = response.json()
        clone = self.__api__.simulations.get(duplication_response['simulation']['id'])

        return clone


class SimulationEndpointApi(
    mixins.ListApiMixin[Simulation],
    mixins.CreateApiMixin[Simulation],
    mixins.GetApiMixin[Simulation],
    mixins.PatchApiMixin[Simulation],
    mixins.DeleteApiMixin,
    BaseEndpointApi[Simulation],
):
    API_PATH = 'simulations'
    IMPORT_PATH = 'import'
    EXPORT_PATH = 'export'
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

    @staticmethod
    def _resolve_json_import_format_content(
        content: SimulationImportPayloadContent,
    ) -> Dict[str, object]:
        """
        Resolves given `content` into a JSON object.

        :Raises:
        - `JSONDecodeError` - `content` is not a valid JSON document
        - `ValueError` - resolved `content` is not a JSON object
        - `FileNotFoundError` - topology file does not exist at provided path
        """
        if isinstance(content, TextIOBase):
            resolved_content = json.load(content)
        elif isinstance(content, Path):
            with content.open('r') as content_file:
                resolved_content = json.load(content_file)
        elif isinstance(content, str):
            resolved_content = json.loads(content)
        else:
            resolved_content = content

        if not isinstance(resolved_content, dict):
            raise ValueError(
                f'JSON topology format payload content must be an object, got {type(resolved_content)}'
            )

        return resolved_content

    @validate_payload_types
    def create_from(
        self,
        title: str,
        format: TopologyFormatType,
        content: SimulationImportPayloadContent,
        organization: Optional[Union[Organization, PrimaryKey]] = None,
    ) -> Simulation:
        """
        Creates a simulation using a supported topology format. Currently supported format is `JSON`.

        :Raises:
        - `JSONDecodeError` - `content` is not a valid JSON document (when format is set to `JSON`)
        - `ValueError` - `content` value does not match `format`
        - `FileNotFoundError` - topology file does not exist at provided path
        """
        payload = cast(
            DataDict,
            TopologyFormat(
                title=title,
                format=format,
                content=IMPORT_FORMAT_CONTENT_HANDLERS[format](content),
            ),
        )
        if organization is not None:
            payload['organization'] = organization
        response = self.__api__.client.post(
            join_urls(self.url, self.IMPORT_PATH),
            data=mixins.serialize_payload(payload),
        )
        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)
        import_result = cast(SimulationImportResponse, response.json())

        return self.get(import_result['id'])

    @validate_payload_types
    def export(
        self,
        simulation: Union[Simulation, PrimaryKey],
        format: TopologyFormatType,
        image_ids: bool = False,
    ) -> TopologyFormatContent:
        """
        Exports an existing simulation into a desired topology format.

        :Arguments:
        - `format`: desired output format (currently supported format is `JSON`)
        - `image_ids`: whether to return image IDs instead of names
        """
        pk = str(simulation.__pk__ if isinstance(simulation, Simulation) else simulation)
        response = self.__api__.client.get(
            join_urls(self.url, pk, self.EXPORT_PATH),
            params={
                'topology_format': format,
                'image_ids': image_ids,
            },
        )
        raise_if_invalid_response(response, status_code=HTTPStatus.OK)

        return cast(TopologyFormat, response.json())['content']


IMPORT_FORMAT_CONTENT_HANDLERS: Dict[
    TopologyFormatType, Callable[[SimulationImportPayloadContent], TopologyFormatContent]
] = {
    'JSON': SimulationEndpointApi._resolve_json_import_format_content,
}
