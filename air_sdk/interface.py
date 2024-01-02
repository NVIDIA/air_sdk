# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Interface module
"""

from . import util
from .air_model import AirModel


class Interface(AirModel):
    """
    View an Interface

    ### json
    Returns a JSON string representation of the interface

    ### refresh
    Syncs the interface with all values returned by the API
    """

    _deletable = False
    _updatable = False

    def __repr__(self):
        if self._deleted or not self.name:
            return super().__repr__()
        return f'<Interface {self.name} {self.id}>'


class InterfaceApi:
    """High-level interface for the Interface API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/interface/'

    def get(self, interface_id, **kwargs):
        """
        Get an existing interface

        Arguments:
            interface_id (str): Interface ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Interface`](/docs/interface)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.interfaces.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Interface eth0 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{interface_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Interface(self, **res.json())

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing interfaces

        Arguments:
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        list

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.interfaces.list()
        [<Interface eth0 c51b49b6-94a7-4c93-950c-e7fa4883591>, <Interface eth1 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """
        # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Interface(self, **interface) for interface in res.json()]
