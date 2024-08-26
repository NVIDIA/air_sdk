# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
SimulationNode module
"""

import json
from functools import wraps
from typing import Callable, Dict, Optional, TypeVar, Literal, Union

from . import util
from .air_model import AirModel, AirModelAPI
from .userconfig import UserConfig

CloudInitAssignmentFields = Literal['user_data', 'meta_data']
CloudInitAssignmentResponseFields = Union[
    CloudInitAssignmentFields, Literal['simulation_node', 'user_data_name', 'meta_data_name']
]
CloudInitAssignment = Dict[CloudInitAssignmentFields, Optional[str]]
CloudInitAssignmentResponse = Dict[CloudInitAssignmentResponseFields, Optional[str]]


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

    def __init__(self, api, **kwargs):
        super().__init__(api, **kwargs)

        # inject v2 functionalities for ease of use
        self_v2_api = _SimulationNodeAPI(self._api.client)
        self_v2 = self_v2_api.model(self_v2_api)

        TMethod = TypeVar('TMethod', bound='Callable')

        def _with_updated_v2(method: TMethod) -> TMethod:
            """Updates mirrored v2 SimulatedNode with v1 data."""

            @wraps(method)
            def _wrapper(*args, **kwargs):
                self_v2._load(**json.loads(self.json()))
                return method(*args, **kwargs)

            return _wrapper

        self.get_cloud_init_assignment = _with_updated_v2(self_v2.get_cloud_init_assignment)
        self.set_cloud_init_assignment = _with_updated_v2(self_v2.set_cloud_init_assignment)

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


class _v2:
    """Temporary private class for v2 related SimulationNode resources."""

    class SimulationNode(AirModel):
        """Manage a v2 SimulationNode."""

        CLOUD_INIT_PATH = 'cloud-init'

        def get_cloud_init_assignment(self) -> CloudInitAssignmentResponse:
            """Returns current state of cloud-init script assignments for the node."""

            url = util.url_path_join(
                self._api.parsed_url, self.id, self.CLOUD_INIT_PATH, trailing_slash=True
            ).geturl()
            response = self._api.client.get(url)
            util.raise_if_invalid_response(response, data_type=dict)

            return response.json()

        def set_cloud_init_assignment(
            self, script_mapping: CloudInitAssignment
        ) -> CloudInitAssignmentResponse:
            """
            Edits cloud-init script assignment for the node as defined in `script_mapping`.
            Returns new state of cloud-init script assignments for the node.

            Any combination of script keys can be provided within `script_mapping`.
            Explicit `None` as a value for a key will clear the assignment for that specific script.

            Example:
            ```
            # only sets user-data
            node.set_cloud_init_assignment({
                'user_data': my_script
            })

            # sets user-data, clears assignment for meta-data
            node.set_cloud_init_assignment({
                'user_data': my_script,
                'meta_data': None
            })

            # identical to `node.get_cloud_init_assignment()`
            node.set_cloud_init_assignment({})
            ```
            """

            patch_payload: CloudInitAssignment = {}
            for script_type in [
                script_type for script_type in script_mapping if script_type in ['user_data', 'meta_data']
            ]:
                script = script_mapping[script_type]
                if isinstance(script, UserConfig):
                    patch_payload[script_type] = script.id
                else:
                    patch_payload[script_type] = script

            if not patch_payload:
                return self.get_cloud_init_assignment()

            url = util.url_path_join(
                self._api.parsed_url, self.id, self.CLOUD_INIT_PATH, trailing_slash=True
            ).geturl()
            response = self._api.client.patch(url, json=patch_payload)
            util.raise_if_invalid_response(response, data_type=dict)

            return response.json()


class _SimulationNodeAPI(AirModelAPI[_v2.SimulationNode]):
    """High-level interface for the SimulationNode v2 API."""

    API_VERSION = 2
    API_PATH = 'simulations/nodes'
