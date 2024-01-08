# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Simulation module
"""

import io
import os

from . import user_preference, util
from .air_model import AirModel


class Simulation(AirModel):
    """
    Manage a Simulation

    ### json
    Returns a JSON string representation of the simulation

    ### refresh
    Syncs the simulation with all values returned by the API

    ### update
    Update the simulation with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """

    _deletable = False

    def __repr__(self):
        if self._deleted or not self.title:
            return super().__repr__()
        return f"<Simulation '{self.title}' {self.id}>"

    def create_service(self, name, interface, dest_port, **kwargs):
        """
        Create a new service for this simulation

        Arguments:
            name (str): Name of the service
            interface (str | `SimulationInterface`): Interface that the service should be created
                for. This can be provided in one of the following formats:
                - [`SimulationInterface`](/docs/simulation-interface) object
                - ID of a [`SimulationInterface`](/docs/simulation-interface)
                - String in the format of 'node_name:interface_name'
            dest_port (int): Service port number
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        [`Service`](/docs/service)

        Example:
        ```
        >>> simulation.create_service('myservice', 'oob-mgmt-server:eth0', 22, service_type='ssh')
        <Service myservice cc18d746-4cf0-4dd3-80c0-e7df68bbb782>
        >>> simulation.create_service('myservice', simulation_interface, 22, service_type='ssh')
        <Service myservice 9603d0d5-5526-4a0f-91b8-a600010d0091>
        ```
        """
        service = self._api.client.services.create(
            simulation=self.id, name=name, interface=interface, dest_port=dest_port, **kwargs
        )
        self.refresh()
        return service

    def add_permission(self, email, **kwargs):
        """
        Adds permission for a given user to this simulation.

        Arguments:
            email (str): Email address of the user being given permission
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        [`Permission`](/docs/permission)

        Example:
        ```
        >>> simulation.add_permission('mrobertson@nvidia.com', write_ok=True)
        <Permission 217bea68-7048-4262-9bbc-b98ab16c603e>
        ```
        """
        return self._api.client.permissions.create(email=email, simulation=self.id, **kwargs)

    @util.required_kwargs(['action'])
    def control(self, **kwargs):
        """
        Sends a control command to the simulation.

        Arguments:
            action (str): Control command
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        dict: Response JSON

        Example:
        ```
        >>> simulation.control(action='destroy')
        {'result': 'success'}
        ```
        """
        url = f'{self._api.url}{self.id}/control/'
        res = self._api.client.post(url, json=kwargs)
        util.raise_if_invalid_response(res)
        return res.json()

    def load(self):
        """Alias for `start()`"""
        self.start()

    def start(self):
        """Start/load the simulation"""
        self.control(action='load')
        self.refresh()

    def stop(self):
        """Alias for `store()`"""
        self.store()

    def store(self):
        """Store and power off the simulation"""
        self.control(action='store')
        self.refresh()

    def delete(self, **kwargs):
        """Delete the simulation"""
        self.control(action='destroy', **kwargs)
        self._deleted = True

    def preferences(self, **kwargs):
        """
        Returns your account preferences for the simulation

        Arguments:
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`UserPreference`](/docs/userpreference)

        Example:
        ```
        >>> simulation.preferences()
        {"show": true}
        ```
        """
        res = self._api.client.get(
            f'{self._api.url.replace("v1", "v2")}{self.id}/preferences/', params=kwargs
        )
        util.raise_if_invalid_response(res)
        return user_preference.UserPreference(self._api, _model=self, _version_override='2', **res.json())


class SimulationApi:
    """High-level interface for the Simulation API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/simulation/'

    def _create_v1(self, **kwargs):
        return self.client.post(self.url, json=kwargs)

    def _create_v2(self, **kwargs):
        topology_data = kwargs['topology_data']
        if isinstance(kwargs['topology_data'], io.IOBase):
            topology_data = kwargs['topology_data'].read()
        elif os.path.isfile(kwargs['topology_data']):
            with open(kwargs['topology_data'], 'r', encoding='utf-8') as data_file:
                topology_data = data_file.read()
        return self.client.post(self.url.replace('v1', 'v2'), json={**kwargs, 'topology_data': topology_data})

    @util.deprecated('SimulationApi.list()')
    def get_simulations(self):  # pylint: disable=missing-function-docstring
        return self.list()

    @util.deprecated('SimulationApi.get()')
    def get_simulation(self, simulation_id):  # pylint: disable=missing-function-docstring
        return self.get(simulation_id)

    @util.deprecated('SimulationApi.create()')
    def create_simulation(self, **kwargs):  # pylint: disable=missing-function-docstring
        return self.create(**kwargs)

    @util.deprecated('Simulation.update()')
    def update_simulation(self, simulation_id, data):  # pylint: disable=missing-function-docstring
        sim = self.get(simulation_id)
        sim.update(**data)

    def duplicate(self, simulation, **kwargs):
        """
        Duplicate/clone an existing simulation

        Arguments:
            simulation (str | `Simulation`): Simulation or ID of the snapshot to be duplicated
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        ([`Simulation`](/docs/simulation), dict): Newly created simulation and response JSON

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.simulations.duplicate(simulation=simulation)
        <Simulation my_sim 5ff3f0dc-7db8-4938-8257-765c8e48623a>
        ```
        """
        sim = simulation
        if isinstance(sim, str):
            sim = self.get(simulation)
        kwargs['action'] = 'duplicate'
        response = sim.control(**kwargs)
        return Simulation(self, **response['simulation']), response

    @util.deprecated('Simulation.control()')
    def control(self, simulation_id, action, **kwargs):  # pylint: disable=missing-function-docstring
        sim = self.get(simulation_id)
        return sim.control(action=action, **kwargs)

    def get_citc_simulation(self):
        """
        Get the active CITC reference simulation

        Returns:
        [`Simulation`](/docs/simulation)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.simulations.get_citc_simulation()
        <Simulation my_sim b9125419-7c6e-41db-bba9-7d647d63943e>
        ```
        """
        url = self.url + 'citc/'
        res = self.client.get(url)
        util.raise_if_invalid_response(res)
        return Simulation(self, **res.json())

    def get(self, simulation_id, **kwargs):
        """
        Get an existing simulation

        Arguments:
            simulation_id (str): Simulation ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Simulation`](/docs/simulation)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.simulations.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Simulation my_sim 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{simulation_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Simulation(self, **res.json())

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing simulations

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
        >>> air.simulations.list()
        [<Simulation sim1 c51b49b6-94a7-4c93-950c-e7fa4883591>, <Simulation sim2 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """  # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Simulation(self, **simulation) for simulation in res.json()]

    @util.required_kwargs([('topology', 'topology_data')])
    def create(self, **kwargs):
        """
        Create a new simulation. The caller must provide either `topology` or `topology_data`.

        Arguments:
            topology (str | `Topology`, optional): `Topology` or ID
            topology_data (str | fd, optional): Topology in DOT format. This can be passed as a string
                containing the raw DOT data, a path to the DOT file on your local disk,
                or as a file descriptor for a local file
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        [`Simulation`](/docs/simulation)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.simulations.create(topology=topology, title='my_sim')
        <Simulation my_sim 01298e0c-4ef1-43ec-9675-93160eb29d9f>
        >>> air.simulations.create(topology_data='/tmp/my_net.dot', organization=my_org)
        <Simulation my_sim c0a4c018-0b85-4439-979d-9814166aaeac>
        >>> air.simulations.create(topology_data='graph "my_sim" { "server1" [ function="server" os="generic/ubuntu2204"] }', organization=my_org)
        <Simulation my_sim b9c0c68e-d4bd-4e9e-8a49-9faf41efaf70>
        >>> air.simulations.create(topology_data=open('/tmp/my_net.dot', 'r', encoding='utf-8')), organization=my_org)
        <Simulation my_sim 86162934-baa7-4d9a-a826-5863f92b03ef>
        ```
        """
        util.validate_timestamps(
            'Simulation created', expires_at=kwargs.get('expires_at'), sleep_at=kwargs.get('sleep_at')
        )
        if kwargs.get('topology'):
            res = self._create_v1(**kwargs)
        else:
            res = self._create_v2(**kwargs)
        util.raise_if_invalid_response(res, status_code=201)
        return Simulation(self, **res.json())
