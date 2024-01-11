# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Topology module
"""

import io
import os

from . import util
from .air_model import AirModel
from .logger import air_sdk_logger as logger


class Topology(AirModel):
    """
    Manage a Topology

    ### delete
    Delete the topology. Once successful, the object should no longer be used and will raise
    [`AirDeletedObject`](/docs/exceptions) when referenced.

    Raises:
    [`AirUnexpectedResposne`](/docs/exceptions) - Delete failed

    ### json
    Returns a JSON string representation of the topology

    ### refresh
    Syncs the topology with all values returned by the API

    ### update
    Update the topology with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """

    _ignored_update_fields = ['links', 'nodes']

    def __repr__(self):
        if self._deleted or not self.name:
            return super().__repr__()
        return f'<Topology {self.name} {self.id}>'

    def add_permission(self, email, **kwargs):
        """
        Adds permission for a given user to this topology.

        Arguments:
            email (str): Email address of the user being given permission
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        [`Permission`](/docs/permission)

        Example:
        ```
        >>> topology.add_permission('mrobertson@nvidia.com', write_ok=True)
        <Permission 217bea68-7048-4262-9bbc-b98ab16c603e>
        ```
        """
        return self._api.client.permissions.create(email=email, topology=self.id, **kwargs)


class TopologyApi:
    """High-level interface for the Topology API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/topology/'

    @util.deprecated('TopologyApi.list()')
    def get_topologies(self):  # pylint: disable=missing-function-docstring
        return self.list()

    @util.deprecated('TopologyApi.create()')
    def create_topology(self, json=None, dot=None):  # pylint: disable=missing-function-docstring
        return self.create(json=json, dot=dot)

    @util.deprecated('Topology.update()')
    def update_topology(self, topology_id, data):  # pylint: disable=missing-function-docstring
        topology = self.get(topology_id)
        return topology.update(**data)

    def get(self, topology_id, **kwargs):
        """
        Get an existing topology

        Arguments:
            topology_id (str): Topology ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Topology`](/docs/topology)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.topologies.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Topology my_network 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{topology_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Topology(self, **res.json())

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing topologies

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
        >>> air.topologies.list()
        [<Topology my_network1 c51b49b6-94a7-4c93-950c-e7fa4883591>, <Topology my_network2 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """  # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Topology(self, **topology) for topology in res.json()]

    @util.required_kwargs([('json', 'dot')])
    def create(self, **kwargs):
        # pylint: disable=line-too-long
        """
        Create a new topology. The caller must provide either `dot` (recommended) or `json`.

        Arguments:
            dot (str | fd, optional): Topology in DOT format. This can be passed as a string
                containing the raw DOT data, a path to the DOT file on your local disk,
                or as a file descriptor for a local file
            json (dict, optional): Topology in JSON format

        Returns:
        [`Topology`](/docs/topology)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.topologies.create(dot='/tmp/my_net.dot')
        <Topology my_net 01298e0c-4ef1-43ec-9675-93160eb29d9f>
        >>> air.topologies.create(dot='graph "my sim" { "server1" [ function="server" os="generic/ubuntu1804"] }')
        <Topology my_net 6256baa8-f54b-4190-85c8-1cc574590080>
        >>> air.topologies.create(dot=open('/tmp/my_net.dot', 'r'))
        <Topology my_net a3d09f12-56ff-4889-8e03-3b714d32c3e5>
        ```
        """
        if kwargs.get('json'):
            res = self.client.post(self.url, json=kwargs['json'])
        else:
            extra_kwargs = [key for key in kwargs if key != 'dot']
            if extra_kwargs:
                logger.warning(
                    f'{extra_kwargs} kwargs are ignored when using using `dot`. '
                    'You may want to use simulations.create() instead.'
                )
            if isinstance(kwargs['dot'], io.IOBase):
                payload = kwargs['dot']
            elif os.path.isfile(kwargs['dot']):
                payload = open(kwargs['dot'], 'r').read()
            else:
                payload = kwargs['dot'].encode('utf-8')
            res = self.client.post(self.url, data=payload, headers={'Content-type': 'text/vnd.graphviz'})
        util.raise_if_invalid_response(res, status_code=201)
        return Topology(self, **res.json())
