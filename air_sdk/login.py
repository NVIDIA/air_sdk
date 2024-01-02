# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Login module
"""

from . import util
from .air_model import AirModel


class Login(AirModel):
    """
    View login information

    ### json
    Returns a JSON string representation of the login info

    ### refresh
    Syncs the login info with all values returned by the API
    """

    _deletable = False
    _updatable = False

    def __repr__(self):
        if self._deleted:
            return super().__repr__()
        return f'<Login {self.id}>'


class LoginApi:
    """High-level interface for the Login API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/login/'

    def get(self, **kwargs):
        """
        Get login information or start an OAuth request. This is equivalent to `login.list()`.

        Arguments:
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Login`](/docs/login)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.login.get()
        <Login>
        ```
        """
        return self.list(**kwargs)

    def list(self, **kwargs):
        """
        Get login information or start an OAuth request. This is equivalent to `login.get()`.

        Arguments:
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Login`](/docs/login)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.login.get()
        <Login>
        ```
        """
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res)
        return Login(self, **res.json())
