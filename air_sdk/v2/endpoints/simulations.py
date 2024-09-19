# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

import json
from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from io import TextIOBase, TextIOWrapper
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypedDict, Union, cast

from air_sdk.util import raise_if_invalid_response
from air_sdk.v2.air_model import AirModel, BaseEndpointApi, DataDict, PrimaryKey
from air_sdk.v2.endpoints import mixins
from air_sdk.v2.endpoints.organizations import Organization
from air_sdk.v2.endpoints.workers import Worker
from air_sdk.v2.utils import join_urls, validate_payload_types

SimulationImportPayloadContent = Union[str, Dict[str, object], Path, TextIOWrapper]


class SimulationImportResponse(TypedDict):
    id: str
    title: str
    organization: Optional[str]
    organization_name: Optional[str]


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
    IMPORT_PATH = 'import'
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
    ) -> Dict[Any, Any]:
        """
        Resolves given `content` into a JSON object.

        :raises:
            `JSONDecodeError` - `content` is not a valid JSON document
            `ValueError` - resolved `content` is not a JSON object
            `FileNotFoundError` - topology file does not exist at provided path
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
        format: str,
        content: SimulationImportPayloadContent,
        organization: Optional[Union[Organization, PrimaryKey]] = None,
    ) -> Simulation:
        """
        Creates a simulation using a supported topology format. Currently supported format is `JSON`.

        :raises:
            `JSONDecodeError` - `content` is not a valid JSON document (when format is set to `JSON`)
            `ValueError` - `format` is unsupported or `content` value does not match `format`
            `FileNotFoundError` - topology file does not exist at provided path
        """
        if format in IMPORT_FORMAT_CONTENT_HANDLERS:
            resolved_content = IMPORT_FORMAT_CONTENT_HANDLERS[format](content)
        else:
            raise ValueError(
                f'`{format}` is not one of supported formats: {list(IMPORT_FORMAT_CONTENT_HANDLERS.keys())}'
            )

        payload: DataDict = {
            'title': title,
            'format': format,
            'content': resolved_content,
        }
        if organization is not None:
            payload['organization'] = organization
        response = self.__api__.client.post(
            join_urls(self.url, self.IMPORT_PATH),
            data=mixins.serialize_payload(payload),
        )
        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)
        import_result = cast(SimulationImportResponse, response.json())

        return self.get(import_result['id'])


IMPORT_FORMAT_CONTENT_HANDLERS: Dict[str, Callable[[SimulationImportPayloadContent], Any]] = {
    'JSON': SimulationEndpointApi._resolve_json_import_format_content
}
