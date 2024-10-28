# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from __future__ import annotations

import json
from http import HTTPStatus
from typing import Optional, Any, TypedDict, List, Callable, Iterator, TYPE_CHECKING, Dict, Generic

from air_sdk.v2.air_json_encoder import AirJSONEncoder
from air_sdk.v2.air_model import PrimaryKey, DataDict, TAirModel_co
from air_sdk.v2.utils import join_urls
from air_sdk.util import raise_if_invalid_response

if TYPE_CHECKING:
    from air_sdk.v2 import AirApi


def serialize_payload(data: Dict[str, Any] | List[Dict[str, Any]]) -> str:
    """Serialize the dictionary of values into json using the AirJSONEncoder."""
    return json.dumps(data, indent=None, separators=(',', ':'), cls=AirJSONEncoder)


class BaseApiMixin:
    """A base class for API Mixins.

    This is primarily used for type hinting.
    """

    __api__: AirApi
    url: str
    load_model: Callable[[DataDict], TAirModel_co]


class PaginatedResponseData(TypedDict):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[DataDict]


class ListApiMixin(BaseApiMixin, Generic[TAirModel_co]):
    """Returns an iterable of model objects.

    Handles pagination in the background.
    """

    def list(self, **params: Any) -> Iterator[TAirModel_co]:
        """Return an iterator of model instances."""
        url = self.url
        # Set up pagination
        next_url = None
        params.setdefault('limit', self.__api__.client.pagination_page_size)
        params = json.loads(serialize_payload(params))  # Accounts for UUIDs and AirModel params
        while url or next_url:
            if isinstance(next_url, str):
                response = self.__api__.client.get(next_url)
            else:
                response = self.__api__.client.get(url, params=params)
            raise_if_invalid_response(response)
            paginated_response_data: PaginatedResponseData = response.json()
            url = None  # type: ignore[assignment]
            next_url = paginated_response_data['next']
            for obj_data in paginated_response_data['results']:
                yield self.load_model(obj_data)


class CreateApiMixin(BaseApiMixin, Generic[TAirModel_co]):
    def create(self, *args: Any, **kwargs: Any) -> TAirModel_co:
        response = self.__api__.client.post(self.url, data=serialize_payload(kwargs))
        raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)
        return self.load_model(response.json())


class GetApiMixin(BaseApiMixin, Generic[TAirModel_co]):
    def get(self, pk: PrimaryKey, **params: Any) -> TAirModel_co:
        detail_url = join_urls(self.url, str(pk))
        response = self.__api__.client.get(detail_url, params=params)
        raise_if_invalid_response(response)
        return self.load_model(response.json())


class PutApiMixin(BaseApiMixin, Generic[TAirModel_co]):
    def put(self, pk: PrimaryKey, **kwargs: Any) -> TAirModel_co:
        response = self.__api__.client.put(join_urls(self.url, str(pk)), data=serialize_payload(kwargs))
        raise_if_invalid_response(response, status_code=HTTPStatus.OK)
        return self.load_model(response.json())


class PatchApiMixin(BaseApiMixin, Generic[TAirModel_co]):
    def patch(self, pk: PrimaryKey, **kwargs: Any) -> TAirModel_co:
        response = self.__api__.client.patch(join_urls(self.url, str(pk)), data=serialize_payload(kwargs))
        raise_if_invalid_response(response, status_code=HTTPStatus.OK)
        return self.load_model(response.json())


class DeleteApiMixin(BaseApiMixin):
    def delete(self, pk: PrimaryKey, **kwargs: Any) -> None:
        """Deletes the instances with the specified primary key."""
        detail_url = join_urls(self.url, str(pk))
        response = self.__api__.client.delete(detail_url, json=kwargs)
        raise_if_invalid_response(response, status_code=HTTPStatus.NO_CONTENT, data_type=None)
