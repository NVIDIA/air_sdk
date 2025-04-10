# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union, Literal, List
from http import HTTPStatus
from air_sdk.v2.endpoints import mixins
from air_sdk.v2.endpoints import Account
from air_sdk.v2.endpoints.organizations import Organization
from air_sdk.v2.air_model import AirModel, BaseEndpointApi, DataDict, PrimaryKey
from air_sdk.v2.utils import join_urls, validate_payload_types
from air_sdk.util import raise_if_invalid_response
from pathlib import Path


DEFAULT_UPLOAD_TIMEOUT = timedelta(minutes=5)


@dataclass(eq=False)
class Image(AirModel):
    id: str = field(repr=False)
    agent_enabled: bool = field(repr=False)
    archived: bool = field(repr=False)
    bios: Optional['Image'] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    bus: str = field(repr=False)
    console_support: Dict[str, Any] = field(repr=False)
    cpu_arch: str = field(repr=False)
    created: datetime = field(repr=False)
    default_username: Optional[str] = field(repr=False)
    default_password: Optional[str] = field(repr=False)
    features: Dict[str, Any] = field(repr=False)
    modified: Optional[datetime] = field(repr=False)
    mountpoint: Optional[str] = field(repr=False)
    minimum_resources: Dict[str, int] = field(repr=False)
    name: Optional[str]
    notes: Optional[str] = field(repr=False)
    organization: Optional[Organization] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    published: Optional[bool] = field(repr=False)
    provider: Optional[str] = field(repr=False)
    release_notes: Optional[str] = field(repr=False)
    simx: Optional[str] = field(repr=False)
    size: int = field(repr=False)
    upload_status: str = field(repr=False)
    uploader: Optional[Account] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    user_manual: Optional[str] = field(repr=False)
    version: str
    can_edit: bool = field(repr=False)
    organization_name: Optional[str]
    uploader_username: Optional[str] = field(repr=False)

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return ImageEndpointApi

    @validate_payload_types
    def upload(self, filepath: str, timeout: Optional[timedelta] = None) -> None:
        """
        Upload an image file.

        :Raises:
        - `FileNotFoundError` - image file does not exist at provided path
        """
        file_path = Path(filepath)
        if timeout is None:
            timeout = DEFAULT_UPLOAD_TIMEOUT
        url = join_urls(self.__api__.images.url_v1, str(self.__pk__), '/upload/')
        with file_path.open('rb') as image_file:
            response = self.__api__.client.put(url, timeout=timeout.total_seconds(), data=image_file)
        raise_if_invalid_response(response, status_code=HTTPStatus.NO_CONTENT, data_type=None)
        self.refresh()

    @validate_payload_types
    def publish(self, contact: str) -> None:
        """
        Publish the image for public use

        :Raises:
        `AirUnexpectedResponse` - Publish failed
        """
        url = join_urls(self.__api__.images.url_v1, str(self.__pk__), '/publish/')
        response = self.__api__.client.put(url, json={'contact': contact})
        raise_if_invalid_response(response, status_code=HTTPStatus.NO_CONTENT, data_type=None)
        self.refresh()

    def unpublish(self):
        """
        Unpublish the image from public use

        :Raises:
        `AirUnexpectedResponse` - Unpublish failed
        """
        url = join_urls(self.__api__.images.url_v1, str(self.__pk__), '/publish/')
        response = self.__api__.client.delete(url)
        raise_if_invalid_response(response, status_code=HTTPStatus.NO_CONTENT, data_type=None)
        self.refresh()

    @validate_payload_types
    def full_update(
        self,
        name: str,
        organization: Union[Organization, PrimaryKey],
        version: str,
        default_username: str,
        default_password: str,
        cpu_arch: Literal['ARM', 'x86'],
        base: Optional[bool] = None,
        agent_enabled: Optional[bool] = None,
        bios: Optional[Union[Image, PrimaryKey]] = None,
        bus: Optional[str] = None,
        features: Optional[DataDict] = None,
        mountpoint: Optional[str] = None,
        minimum_resources: Optional[Dict[str, int]] = None,
        notes: Optional[str] = None,
        provider: Optional[Literal['VM', 'CONTAINER']] = None,
        release_notes: Optional[str] = None,
        user_manual: Optional[str] = None,
        emulation_type: Optional[List[str]] = None,
        emulation_version: Optional[str] = None,
        console_support: Optional[DataDict] = None,
    ) -> None:
        payload: DataDict = {
            'name': name,
            'organization': organization,
            'version': version,
            'default_username': default_username,
            'default_password': default_password,
            'cpu_arch': cpu_arch,
        }
        for key, value in (
            ('base', base),
            ('agent_enabled', agent_enabled),
            ('bios', bios),
            ('bus', bus),
            ('features', features),
            ('organization', organization),
            ('mountpoint', mountpoint),
            ('minimum_resources', minimum_resources),
            ('notes', notes),
            ('provider', provider),
            ('release_notes', release_notes),
            ('user_manual', user_manual),
            ('emulation_type', emulation_type),
            ('emulation_version', emulation_version),
            ('console_support', console_support),
        ):
            if value is not None:  # Don't include optional None fields in payload.
                payload[key] = value

        url = join_urls(self.__api__.images.url_v1, str(self.__pk__))
        response = self.__api__.client.put(url, data=mixins.serialize_payload(payload))
        raise_if_invalid_response(response, status_code=HTTPStatus.OK, data_type=None)
        self.refresh()

    @validate_payload_types
    def update(
        self,
        name: Optional[str] = None,
        organization: Optional[Union[Organization, PrimaryKey]] = None,
        version: Optional[str] = None,
        default_username: Optional[str] = None,
        default_password: Optional[str] = None,
        cpu_arch: Optional[Literal['ARM', 'x86']] = None,
        base: Optional[bool] = None,
        agent_enabled: Optional[bool] = None,
        bios: Optional[Union[Image, PrimaryKey]] = None,
        bus: Optional[str] = None,
        features: Optional[DataDict] = None,
        mountpoint: Optional[str] = None,
        minimum_resources: Optional[Dict[str, int]] = None,
        notes: Optional[str] = None,
        provider: Optional[Literal['VM', 'CONTAINER']] = None,
        release_notes: Optional[str] = None,
        user_manual: Optional[str] = None,
        emulation_type: Optional[List[str]] = None,
        emulation_version: Optional[str] = None,
        console_support: Optional[DataDict] = None,
    ) -> None:
        payload: DataDict = {}
        for key, value in (
            ('name', name),
            ('organization', organization),
            ('version', version),
            ('default_username', default_username),
            ('default_password', default_password),
            ('cpu_arch', cpu_arch),
            ('base', base),
            ('agent_enabled', agent_enabled),
            ('bios', bios),
            ('bus', bus),
            ('features', features),
            ('organization', organization),
            ('mountpoint', mountpoint),
            ('minimum_resources', minimum_resources),
            ('notes', notes),
            ('provider', provider),
            ('release_notes', release_notes),
            ('user_manual', user_manual),
            ('emulation_type', emulation_type),
            ('emulation_version', emulation_version),
            ('console_support', console_support),
        ):
            if value is not None:  # Don't include optional None fields in payload.
                payload[key] = value

        url = join_urls(self.__api__.images.url_v1, str(self.__pk__))
        response = self.__api__.client.patch(url, data=mixins.serialize_payload(payload))
        raise_if_invalid_response(response, status_code=HTTPStatus.OK, data_type=None)
        self.refresh()

    def delete(self):
        url = join_urls(self.__api__.images.url_v1, str(self.__pk__))
        response = self.__api__.client.delete(url)
        raise_if_invalid_response(response, status_code=HTTPStatus.NO_CONTENT, data_type=None)


class ImageEndpointApi(mixins.ListApiMixin[Image], mixins.GetApiMixin[Image], BaseEndpointApi[Image]):
    API_PATH = 'images'
    model = Image

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.url_v1 = join_urls(self.__api__.client.base_url.replace('/api/v2/', '/api/v1/'), 'image')

    @validate_payload_types
    def create(
        self,
        name: str,
        organization: Union[Organization, PrimaryKey],
        version: str,
        default_username: str,
        default_password: str,
        cpu_arch: Literal['ARM', 'x86'],
        base: Optional[bool] = None,
        agent_enabled: Optional[bool] = None,
        bios: Optional[Union[Image, PrimaryKey]] = None,
        bus: Optional[str] = None,
        features: Optional[DataDict] = None,
        mountpoint: Optional[str] = None,
        minimum_resources: Optional[Dict[str, int]] = None,
        notes: Optional[str] = None,
        provider: Optional[Literal['VM', 'CONTAINER']] = None,
        release_notes: Optional[str] = None,
        user_manual: Optional[str] = None,
        emulation_type: Optional[List[str]] = None,
        emulation_version: Optional[str] = None,
        console_support: Optional[DataDict] = None,
    ) -> Image:
        payload: DataDict = {
            'name': name,
            'organization': organization,
            'version': version,
            'default_username': default_username,
            'default_password': default_password,
            'cpu_arch': cpu_arch,
        }
        for key, value in (
            ('base', base),
            ('agent_enabled', agent_enabled),
            ('bios', bios),
            ('bus', bus),
            ('features', features),
            ('organization', organization),
            ('mountpoint', mountpoint),
            ('minimum_resources', minimum_resources),
            ('notes', notes),
            ('provider', provider),
            ('release_notes', release_notes),
            ('user_manual', user_manual),
            ('emulation_type', emulation_type),
            ('emulation_version', emulation_version),
            ('console_support', console_support),
        ):
            if value is not None:  # Don't include optional None fields in payload.
                payload[key] = value

        response = self.__api__.client.post(self.url_v1, data=mixins.serialize_payload(payload))
        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)
        return self.get(response.json()['id'])

    def delete(self, pk: PrimaryKey) -> None:
        """Deletes the instances with the specified primary key."""
        detail_url = join_urls(self.url_v1, str(pk))
        response = self.__api__.client.delete(detail_url)
        raise_if_invalid_response(response, status_code=HTTPStatus.NO_CONTENT, data_type=None)
