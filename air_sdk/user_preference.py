# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
UserPreference module
"""

import json
import re

from .air_model import AirModel
from . import util


class UserPreference(AirModel):
    """
    A collection of your user preferences, which may be global for your account or specific to a single
    simulation.

    ### json
    Returns a JSON string representation of the preferences object

    ### refresh
    Syncs the key with all values returned by the API
    """

    _deletable = False

    def __init__(self, api, **kwargs):
        _model = kwargs.pop('_model', None)
        _version_override = kwargs.pop('_version_override', None)
        super().__init__(api, **kwargs)
        self._model = _model
        self._version_override = _version_override
        self._url = self._build_url()

    def __repr__(self):
        return json.dumps(self.preferences)

    def __setattr__(self, name, value):
        if not getattr(self, '_url', None):
            return super().__setattr__(name, value)
        if self.preferences.get(name) != value:
            res = self._api.client.patch(self._url, json={name: value})
            util.raise_if_invalid_response(res)
        self.preferences[name] = value
        return None

    def _build_url(self):
        url = self._api.url
        if self._model:
            url += f'{self._model.id}/'
        url += 'preferences/'
        if self._version_override:
            url = re.sub(r'/v\d/', f'/v{self._version_override}/', url)
        return url

    def refresh(self):
        """Syncs the object with all values returned by the API"""
        instance = self._model or self._api
        self._load(**instance.preferences().__dict__)

    def update(self, **kwargs):
        """
        Update the object with the provided data

        Arguments:
            kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
        """
        self.refresh()
        self.preferences.update(kwargs)
        res = self._api.client.put(self._url, json=self.__dict__)
        util.raise_if_invalid_response(res)
