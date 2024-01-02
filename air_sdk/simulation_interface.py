# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
SimulationInterface module
"""

from . import util
from .air_model import AirModel


class SimulationInterface(AirModel):
    """
    Manage a SimulationInterface

    ### json
    Returns a JSON string representation of the simulation interface

    ### refresh
    Syncs the simulation interface with all values returned by the API

    ### update
    Update the simulation interface with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """

    _deletable = False

    def __repr__(self):
        if self._deleted:
            return super().__repr__()
        return f'<SimulationInterface {self.id}>'


class SimulationInterfaceApi:
    """High-level interface for the SimulationInterface API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/simulation-interface/'

    @util.deprecated('SimulationInterfaceApi.list()')
    def get_simulation_interfaces(self, simulation_id='', original_id=''):  # pylint: disable=missing-function-docstring
        return self.list(simulation=simulation_id, original=original_id)

    def get(self, simulation_interface_id, **kwargs):
        """
        Get an existing simulation interface

        Arguments:
            simulation_interface_id (str): SimulationInterface ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`SimulationInterface`](/docs/simulationinterface)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.simulation_interfaces.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <SimulationInterface 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{simulation_interface_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return SimulationInterface(self, **res.json())

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing simulation interfaces

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
        >>> air.simulation_interfaces.list()
        [<SimulationInterface c51b49b6-94a7-4c93-950c-e7fa4883591>, <SimulationInterface 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """  # pylint: enable=line-too-long
        if kwargs.get('interface'):
            kwargs['original'] = kwargs['interface']
            del kwargs['interface']
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [SimulationInterface(self, **simulation_interface) for simulation_interface in res.json()]
