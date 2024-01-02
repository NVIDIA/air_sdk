# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Node module
"""

from . import util
from .air_model import AirModel


class Node(AirModel):
    """
    Manage a Node

    ### delete
    Delete the node. Once successful, the object should no longer be used and will raise
    [`AirDeletedObject`](/docs/exceptions) when referenced.

    Raises:
    [`AirUnexpectedResposne`](/docs/exceptions) - Delete failed

    ### json
    Returns a JSON string representation of the node

    ### refresh
    Syncs the node with all values returned by the API

    ### update
    Update the node with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """

    _ignored_update_fields = ['interfaces']

    def __repr__(self):
        if self._deleted or not self.name:
            return super().__repr__()
        return f'<Node {self.name} {self.id}>'


class NodeApi:
    """High-level interface for the Node API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/node/'

    @util.deprecated('NodeApi.list()')
    def get_nodes(self, simulation_id=''):  # pylint: disable=missing-function-docstring
        return self.list(simulation=simulation_id)

    def get(self, node_id, **kwargs):
        """
        Get an existing node

        Arguments:
            node_id (str): Node ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Node`](/docs/node)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.nodes.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Node server 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        if kwargs.get('simulation_id'):
            kwargs['simulation'] = kwargs['simulation_id']
            del kwargs['simulation_id']
        url = f'{self.url}{node_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Node(self, **res.json())

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing nodes

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
        >>> air.nodes.list()
        [<Node server c51b49b6-94a7-4c93-950c-e7fa4883591>, <Node switch 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """  # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Node(self, **node) for node in res.json()]

    @util.required_kwargs(['name', 'topology'])
    def create(self, **kwargs):
        """
        Create a new node

        Arguments:
            name (str): Node name
            topology (str | `Topology`): `Topology` or ID
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        [`Node`](/docs/node)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.nodes.create(name='server', topology=topology)
        <Node server 01298e0c-4ef1-43ec-9675-93160eb29d9f>
        ```
        """
        res = self.client.post(self.url, json=kwargs)
        util.raise_if_invalid_response(res, status_code=201)
        return Node(self, **res.json())
