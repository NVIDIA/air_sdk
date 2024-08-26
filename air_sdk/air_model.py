# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Base classes for AIR object models
"""

from __future__ import annotations

import json
import re
from abc import ABC
from datetime import date, datetime
from http import HTTPStatus
from typing import TYPE_CHECKING, Dict, Generic, List, Optional, Type, TypeVar, Union, get_args
from urllib.parse import urlparse


from . import util
from .exceptions import AirObjectDeleted

# `AirApi` exposes resource APIs via its properties
# this means that we can not import `AirApi` for type hinting purposes as this will cause a circular import
# therefore, we only import `AirApi` during type checking
if TYPE_CHECKING:  # pragma: no cover
    from typing import Literal

    from .air_api import AirApi

TAirModel = TypeVar('TAirModel', bound='AirModel')


class AirModel:
    """Base class for AIR object models"""

    model_keys = {
        'account': 'accounts',
        'base_simulation': 'simulations',
        'bios': 'images',
        'connection': 'links',
        'creator': 'accounts',
        'demo': 'demos',
        'interface': 'simulation_interfaces',
        'interfaces': {
            'Node': 'interfaces',
            'SimulationNode': 'simulation_interfaces',
            'Link': 'interfaces',
        },
        'job': 'jobs',
        'last_worker': 'worker',
        'node': {
            'Interface': 'nodes',
            'NodeInstruction': 'simulation_nodes',
            'SimulationInterface': 'simulation_nodes',
            'TopologyInstruction': 'nodes',
        },
        'nodes': 'simulation_nodes',
        'original': {
            'SimulationInterface': 'interfaces',
            'SimulationNode': 'nodes',
        },
        'organization': 'organizations',
        'os': 'images',
        'preferred_worker': 'workers',
        'services': 'services',
        'simulation': 'simulations',
        'topology': 'topologies',
        'worker': 'workers',
        'fleet': 'fleets',
        'userconfig': 'userconfigs',
    }

    def __init__(self, api: AirModelAPI, **kwargs):
        self._deleted = False
        super().__setattr__('_updatable', getattr(self, '_updatable', True))
        super().__setattr__('_deletable', getattr(self, '_deletable', True))
        self._api = api
        self._load(**kwargs)

    def _load(self, **kwargs):
        for key, value in kwargs.items():
            _value = value
            datetime_obj = util.is_datetime_str(value)
            if datetime_obj:
                _value = datetime_obj
            if key in self.model_keys and value:
                if isinstance(value, list) and not isinstance(value, LazyLoadedList):
                    _value = LazyLoadedList(
                        [LazyLoaded(id=_get_item_id(item), model=self._get_model_key(key)) for item in value],
                        self._api,
                    )
                elif isinstance(value, (LazyLoaded, LazyLoadedList)):
                    _value = value
                elif value.startswith('http'):
                    _value = LazyLoaded(id=_value.split('/')[6], model=self._get_model_key(key))
                else:
                    _value = LazyLoaded(id=_value, model=self._get_model_key(key))
            super().__setattr__(key, _value)

    def __repr__(self):
        repr_str = super().__repr__()
        if self._deleted:
            repr_str = f'<Deleted Object ({repr_str})>'
        return repr_str

    def __getattribute__(self, name):
        value = super().__getattribute__(name)
        if name == '_deleted':
            return value
        if self._deleted:
            raise AirObjectDeleted(type(self))
        if isinstance(value, LazyLoaded):
            value = getattr(self._api.client, value.model).get(value.id)
            super().__setattr__(name, value)
        return value

    def __setattr__(self, name, value):
        if name == '_deleted' or not self._updatable:
            return super().__setattr__(name, value)
        try:
            original = super().__getattribute__(name)
            api = super().__getattribute__('_api')
            id = super().__getattribute__('id')  # pylint: disable=redefined-builtin
        except AttributeError:
            original = None
            api = None
            id = None
        if not name.startswith('_') and api and id and original != value:
            self._patch(name, value)
        return super().__setattr__(name, value)

    def _get_model_key(self, key):
        value = self.model_keys[key]
        if isinstance(value, dict):
            value = self.model_keys[key][self.__class__.__name__]
        return value

    def _patch(self, key, value):
        url = f'{self._api.url}{self.id}/'
        res = self._api.client.patch(url, json={key: value})
        util.raise_if_invalid_response(res)

    def update(self, **kwargs):
        """
        Update the object with the provided data

        Arguments:
            kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
        """
        if not self._updatable:
            raise NotImplementedError(f'{self.__class__.__name__} does not support updates')
        url = f'{self._api.url}{self.id}/'
        ignored_fields = getattr(self, '_ignored_update_fields', None)
        args = kwargs
        if ignored_fields:
            allowed_payload = {}
            for key, value in kwargs.items():
                if key not in ignored_fields:
                    allowed_payload[key] = value
            args = allowed_payload
        res = self._api.client.patch(url, json=args)
        util.raise_if_invalid_response(res)

    def delete(self, **kwargs):
        """
        Delete the object. Once successful, the object should no longer be used and will raise
        [`AirDeletedObject`](/docs/exceptions) when referenced.

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - Delete failed
        """
        if not self._deletable:
            raise NotImplementedError(f'{self.__class__.__name__} does not support deletes')
        url = f'{self._api.url}{self.id}/'
        res = self._api.client.delete(url, json=kwargs)
        util.raise_if_invalid_response(res, status_code=204, data_type=None)
        self._deleted = True

    def refresh(self):
        """Syncs the object with all values returned by the API"""
        self._load(**self._api.get(self.id).__dict__)

    def json(self):
        """Returns a JSON string representation of the object"""
        payload = {}
        for key, value in self.__dict__.items():
            if isinstance(value, (datetime, date)):
                value = value.isoformat()
            if key.startswith('_'):
                continue
            if callable(value):
                continue
            if isinstance(value, (AirModel, LazyLoaded)):
                payload[key] = value.id
            elif isinstance(value, LazyLoadedList):
                payload[key] = [obj.id for obj in value.__iter__(skip_load=True)]
            else:
                payload[key] = value
        return json.dumps(payload)


class LazyLoaded:
    """A lazy object whose data will be loaded later"""

    def __init__(self, id, model):  # pylint: disable=redefined-builtin
        self.id = id
        self.model = model

    def __repr__(self):
        model_str = self.model.capitalize()
        if model_str == 'Topologies':
            model_str = 'Topology'
        elif model_str.endswith('s'):
            model_str = model_str[:-1]
        return f'<air_sdk.air_model.LazyLoaded {model_str} {self.id}>'


class LazyLoadedList(list):
    """A list whose items are LazyLoaded"""

    def __init__(self, items, api):
        self._api = api
        super().__init__(items)

    def __getitem__(self, index):
        value = super().__getitem__(index)
        if isinstance(value, LazyLoaded):
            value = getattr(self._api.client, value.model).get(value.id)
            self[index] = value
        return value

    def __iter__(self, skip_load=False):
        items = super().__iter__()
        for item in items:
            if isinstance(item, LazyLoaded) and not skip_load:
                yield getattr(self._api.client, item.model).get(item.id)
            else:
                yield item


def _get_item_id(item):
    if isinstance(item, dict):
        return item['id']
    try:
        return item.split('/')[6]
    except (AttributeError, IndexError):
        return item


class AirModelAPI(ABC, Generic[TAirModel]):
    """
    Generic class for representing Air resource APIs. Implements functionalities which are common across all resources.

    Usage example:
    ```
    class UserConfigAPI(AirModelAPI[UserConfig]):
        \"\"\"High-level interface for the UserConfig API.\"\"\"

        API_VERSION = 2
        API_PATH = 'userconfigs'
    ```
    """

    API_VERSION: int = 1
    API_PATH: Optional[str] = None

    def __init__(self, client: AirApi):
        if not self.API_PATH:
            raise AttributeError('Model API path `API_PATH` is not properly defined')

        self.client = client
        parsed_url = urlparse(self.client.api_url, allow_fragments=False)
        parsed_url = parsed_url._replace(
            path=re.sub(
                pattern=r'/v[1-2](/|$)?', repl=f'/v{self.API_VERSION}\\1', string=parsed_url.path, count=1
            )
        )
        self.parsed_url = util.url_path_join(parsed_url, self.API_PATH, trailing_slash=False)
        self.url = util.url_path_join(self.parsed_url, trailing_slash=True).geturl()

    @property
    def model(self) -> Type[TAirModel]:
        """Returns the respective model for this API."""

        return get_args(self.__orig_bases__[0])[0]

    def get(self, id: str, **kwargs) -> TAirModel:
        """
        Get an existing instance of a resource by ID.

        Arguments:
            id (str): Instance ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Raises:
        `AirUnexpectedResponse` - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.organizations.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Organization NVIDIA 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """

        url = util.url_path_join(self.parsed_url, id, trailing_slash=True).geturl()
        response = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(response)

        return self.model(self, **response.json())

    def list(self, **kwargs) -> List[TAirModel]:
        """
        List existing instances of a resource.

        Arguments:
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Raises:
        `AirUnexpectedResponse` - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.organizations.list()
        [<Organization NVIDIA c51b49b6-94a7-4c93-950c-e7fa4883591>, <Organization Customer 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """

        url = util.url_path_join(self.parsed_url, trailing_slash=True).geturl()
        response = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(response, data_type=(list, dict))

        # response can either be a list of instances or a paginated response containing the first page of instances
        # TODO iterate pages
        parsed_response: Union[List[Dict], Dict[Literal['results'], List[Dict]]] = response.json()
        if isinstance(parsed_response, list):
            models_data = parsed_response
        else:
            models_data = parsed_response['results']

        return [self.model(self, **model_data) for model_data in models_data]

    def create(self, **kwargs) -> TAirModel:
        """
        Create a new instance of a resource.

        Arguments:
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Raises:
        `AirUnexpectedResponse` - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.organizations.create(name='NVIDIA', members=[{'username': 'user1@nvidia.com', 'roles': ['Organization Admin']}, {'username': 'user2@nvidia.com'}])
        <Organization NVIDIA 01298e0c-4ef1-43ec-9675-93160eb29d9f>
        """

        url = util.url_path_join(self.parsed_url, trailing_slash=True).geturl()
        response = self.client.post(url, json=kwargs)
        util.raise_if_invalid_response(response, status_code=HTTPStatus.CREATED)

        return self.model(self, **response.json())
