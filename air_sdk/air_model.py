# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Base classes for AIR object models
"""
from datetime import date, datetime
import json

from . import util
from .exceptions import AirObjectDeleted


class AirModel:
    """Base class for AIR object models"""

    model_keys = {
        'account': 'accounts',
        'base_simulation': 'simulations',
        'bios': 'images',
        'connection': 'links',
        'demo': 'demos',
        'interface': 'simulation_interfaces',
        'interfaces': {'Node': 'interfaces', 'SimulationNode': 'simulation_interfaces', 'Link': 'interfaces'},
        'job': 'jobs',
        'last_worker': 'worker',
        'node': {
            'Interface': 'nodes',
            'NodeInstruction': 'simulation_nodes',
            'SimulationInterface': 'simulation_nodes',
            'TopologyInstruction': 'nodes',
        },
        'nodes': 'simulation_nodes',
        'original': {'SimulationInterface': 'interfaces', 'SimulationNode': 'nodes'},
        'organization': 'organizations',
        'os': 'images',
        'preferred_worker': 'workers',
        'services': 'services',
        'simulation': 'simulations',
        'topology': 'topologies',
        'worker': 'workers',
        'fleet': 'fleets',
    }

    def __init__(self, api, **kwargs):
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
        self.refresh()
        self.__dict__.update(kwargs)
        payload = self.__dict__
        ignored_fields = getattr(self, '_ignored_update_fields', None)
        if ignored_fields:
            allowed_payload = {}
            for key, value in payload.items():
                if key not in ignored_fields:
                    allowed_payload[key] = value
            payload = allowed_payload
        res = self._api.client.put(url, json=payload)
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
