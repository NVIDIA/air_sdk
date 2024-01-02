# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Marketplace Demo module
"""

from . import util
from .air_model import AirModel


class Marketplace(AirModel):
    """
    Manage marketplace demos

    """

    _updatable = False
    _deletable = False

    def __repr__(self):
        if self._deleted or not self.name:
            return super().__repr__()
        return f"<Marketplace Demo '{self.name}' {self.id}>"


class MarketplaceApi:
    """High-level interface for the Marketplace API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/marketplace/demo/'

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing keys

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
        >>> air.marketplace.list()
        [<Marketplace Demo EVPN Centralized c51b49b6-94a7-4c93-950c-e7fa4883591>]
        ```
        """  # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Marketplace(self, **key) for key in res.json()]

    def get(self, demo_id, **kwargs):
        """
        Get an existing marketplace demo

        Arguments:
            demo_id (str): Demo ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Demo`](/docs/marketplace)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.marketplace.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Marketplace Demo EVPN Centralized 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{demo_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Marketplace(self, **res.json())
