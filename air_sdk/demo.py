# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Demo module
"""

from . import util
from .air_model import AirModel


class Demo(AirModel):
    """
    View Demos
    ### json
    Returns a JSON string representation of the demo

    ### refresh
    Syncs the demo with all values returned by the API
    """

    _deletable = False
    _updatable = False

    def __repr__(self):
        if self._deleted or not self.name:
            return super().__repr__()
        return f"<Demo '{self.name}' {self.id}>"


class DemoApi:
    """High-level interface for the Demo API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/demo/'

    def get(self, demo_id, **kwargs):
        """
        Get an existing demo

        Arguments:
            dmeo_id (str): Demo ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Demo`](/docs/demo)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.demos.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Demo EVPN 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{demo_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Demo(self, **res.json())

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing demos

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
        >>> air.demos.list()
        [<Demo EVPN c51b49b6-94a7-4c93-950c-e7fa4883591>, <Demo Challenges 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """  # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Demo(self, **demo) for demo in res.json()]
