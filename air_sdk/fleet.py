# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Fleet module
"""

from . import util
from .air_model import AirModel


class Fleet(AirModel):
    """
    Manage a Fleet

    ### delete
    Delete the fleet. Once successful, the object should no longer be used and will raise
    [`AirDeletedObject`](/docs/exceptions) when referenced.

    Raises:
    [`AirUnexpectedResposne`](/docs/exceptions) - Delete failed

    ### json
    Returns a JSON string representation of the fleet

    ### refresh
    Syncs the fleet with all values returned by the API

    ### update
    Update the fleet with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """

    def __repr__(self):
        if self._deleted or not self.name:
            return super().__repr__()
        return f'<Fleet {self.name} {self.id}>'


class FleetApi:
    """High-level interface for the Fleet API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/fleet/'
        self.url = self.url.replace('v1', 'v2')

    def get(self, fleet_id, **kwargs):
        """
        Get an existing fleet

        Arguments:
            fleet_id (str): Fleet ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Fleet`](/docs/fleet)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.fleets.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Fleet fleet01 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{fleet_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Fleet(self, **res.json())

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing fleets

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
        >>> air.fleets.list()
        [<Fleet fleet01 c51b49b6-94a7-4c93-950c-e7fa4883591>, <Fleet fleet02 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """  # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=dict)
        res = res.json().get('results')
        return [Fleet(self, **fleet) for fleet in res]

    @util.required_kwargs(['name', 'organization'])
    def create(self, **kwargs):
        # pylint: disable=line-too-long
        """
        Create a new fleet
        Arguments:
            name (str): Name of the fleet
            organization (`Organization` | str): `Organization` or ID associated with the fleet
            prefix (str, optional): Prefix for the fleet's IPv6 addresses
            prefix_length (int, optional): Length of the IPv6 address prefix
            gateway_ipv4 (str, optional): IPv4 gateway address for the fleet
            port_range (str, optional): Range of ports available on the fleet
            container_ipv4_network (str, optional): IPv4 network address for containers in the fleet
            container_prefix (int, optional): Prefix length for container IP addresses
            labels (list, optional): List of labels to assign to the fleet
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
            [`Fleet`](/docs/fleet)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.fleets.create(name='MyFleet', prefix='fd10:1:1::', prefix_length=48, gateway_ipv4='10.0.0.1', port_range='20000-40000', container_ipv4_network='172.16.0.0', container_prefix=16, organization=MyOrganization, labels=['label1', 'label2'])
        <Fleet MyFleet 3dadd54d-583c-432e-9383-a2b0b1d7f221>
        ```
        """  # pylint: enable=line-too-long
        res = self.client.post(self.url, json=kwargs)
        util.raise_if_invalid_response(res, status_code=201)
        return Fleet(self, **res.json())
