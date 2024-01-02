# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
SimulationNode module
"""

from . import util
from .air_model import AirModel


class SimulationNode(AirModel):
    """
    Manage a SimulationNode

    ### json
    Returns a JSON string representation of the simulation node

    ### refresh
    Syncs the simulation node with all values returned by the API

    ### update
    Update the simulation node with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """

    _deletable = False

    def __repr__(self):
        if self._deleted:
            return super().__repr__()
        return f'<SimulationNode {self.id}>'

    @util.required_kwargs(['executor', 'data'])
    def create_instructions(self, **kwargs):
        """
        Create instructions for the `SimulationNode`'s agent to execute

        Arguments:
            data (str | list): Instruction data
            executor (str): Agent executor type
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        dict: Response JSON

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> simulation_node.create_instructions(data='echo foo', executor='shell')
        {'id': '67f73552-ffdf-4e5f-9881-aeae227604a3'}
        ```
        """
        url = f'{self._api.url}{self.id}/instructions/'
        if isinstance(kwargs['data'], list):
            kwargs['data'] = '\n'.join(kwargs['data'])
        res = self._api.client.post(url, json=kwargs)
        util.raise_if_invalid_response(res, status_code=201, data_type=str)
        return {'id': res.json()}

    def list_instructions(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List all instructions for a `SimulationNode`

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
        >>> simulation_node.instructions.list()
        [{'id': '56abc69b-489f-429a-aed9-600f26afc956'}, {'id': '7c9c3449-f071-4bbc-bb42-bef04e44d74e'}]
        ```
        """  # pylint: enable=line-too-long
        url = f'{self._api.url}{self.id}/instructions/'
        res = self._api.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return res.json()

    def delete_instructions(self):
        """
        Delete all instructions for a `SimulationNode`

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - Instruction delete failed

        Example:
        ```
        >>> simulation_node.instructions.delete()
        ```
        """
        url = f'{self._api.url}{self.id}/instructions/'
        res = self._api.client.delete(url)
        util.raise_if_invalid_response(res, status_code=204, data_type=None)

    @util.required_kwargs(['action'])
    def control(self, **kwargs):
        """
        Sends a control command to the `SimulationNode`.

        Arguments:
            action (str): Control command
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        dict: Response JSON

        Example:
        ```
        >>> simulation_node.control(action='reset')
        {'result': 'success'}
        ```
        """
        url = f'{self._api.url}{self.id}/control/'
        res = self._api.client.post(url, json=kwargs)
        util.raise_if_invalid_response(res)
        return res.json()

    def rebuild(self, **kwargs):
        """
        Rebuild the `SimulationNode` back to it's initial state. **All existing data will be lost!**
        """
        self.control(action='rebuild', **kwargs)

    def reset(self, **kwargs):
        """Reset the `SimulationNode`"""
        self.control(action='reset', **kwargs)


class SimulationNodeApi:
    """Wrapper for the SimulationNode API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/simulation-node/'

    @util.deprecated('SimulationNode.update()')
    def update_simulation_node(self, simulation_node_id, data):  # pylint: disable=missing-function-docstring
        node = self.get(simulation_node_id)
        node.update(**data)

    @util.deprecated('SimulationNodeApi.list()')
    def get_simulation_nodes(self, **kwargs):  # pylint: disable=missing-function-docstring
        return self.list(**kwargs)

    def get(self, simulation_node_id, **kwargs):
        """
        Get an existing simulation node

        Arguments:
            simulation_node_id (str): SimulationNode ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`SimulationNode`](/docs/simulationnode)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.simulation_nodes.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <SimulationNode my_sim 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{simulation_node_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return SimulationNode(self, **res.json())

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing simulation nodes

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
        >>> air.simulation_nodes.list()
        [<SimulationNode sim1 c51b49b6-94a7-4c93-950c-e7fa4883591>, <SimulationNode sim2 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """  # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [SimulationNode(self, **simulation_node) for simulation_node in res.json()]
