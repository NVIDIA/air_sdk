# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Service module
"""

from . import util
from .air_model import AirModel


class Service(AirModel):
    """
    Manage a Service

    ### delete
    Delete the service. Once successful, the object should no longer be used and will raise
    [`AirDeletedObject`](/docs/exceptions) when referenced.

    Raises:
    [`AirUnexpectedResposne`](/docs/exceptions) - Delete failed

    ### json
    Returns a JSON string representation of the service

    ### refresh
    Syncs the service with all values returned by the API

    ### update
    Update the service with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """

    def __repr__(self):
        if self._deleted or not self.name:
            return super().__repr__()
        return f'<Service {self.name} {self.id}>'


class ServiceApi:
    """High-level interface for the Service API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/service/'

    @util.deprecated('ServiceApi.list()')
    def get_services(self):  # pylint: disable=missing-function-docstring
        return self.list()

    @util.deprecated('ServiceApi.get()')
    def get_service(self, service_id):  # pylint: disable=missing-function-docstring
        return self.get(service_id)

    @util.deprecated('ServiceApi.create()')
    def create_service(self, simulation_id, name, interface, dest_port, **kwargs):  # pylint: disable=missing-function-docstring
        return self.create(
            simulation=simulation_id, name=name, interface=interface, dest_port=dest_port, **kwargs
        )

    def get(self, service_id, **kwargs):
        """
        Get an existing service

        Arguments:
            service_id (str): Service ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Service`](/docs/service)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.services.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Service SSH 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{service_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Service(self, **res.json())

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing services

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
        >>> air.services.list()
        [<Service SSH c51b49b6-94a7-4c93-950c-e7fa4883591>, <Service HTTP 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """  # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Service(self, **service) for service in res.json()]

    @util.required_kwargs(['name', 'simulation', 'interface'])
    def create(self, **kwargs):
        """
        Create a new service

        Arguments:
            name (str): Service name
            interface (str | `SimulationInterface`): Interface that the service should be created
                for. This can be provided in one of the following formats:
                - [`SimulationInterface`](/docs/simulationinterface) object
                - ID of a [`SimulationInterface`](/docs/simulationinterface)
                - String in the format of 'node_name:interface_name'
            simulation (str | `Simulation`): `Simulation` or ID
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        [`Service`](/docs/service)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.services.create(name='myservice', interface='oob-mgmt-server:eth0', dest_port=22)
        <Service myservice cc18d746-4cf0-4dd3-80c0-e7df68bbb782>
        >>> air.services.create(name='myservice', interface=simulation_interface, dest_port=22)
        <Service myservice 9603d0d5-5526-4a0f-91b8-a600010d0091>
        ```
        """
        if isinstance(kwargs['interface'], str) and ':' in kwargs['interface']:
            kwargs['interface'] = self._resolve_interface(kwargs['interface'], kwargs['simulation'])
        res = self.client.post(self.url, json=kwargs)
        util.raise_if_invalid_response(res, status_code=201)
        return Service(self, **res.json())

    def _resolve_interface(self, interface, simulation):
        try:
            node_name = interface.split(':')[0]
            interface_name = interface.split(':')[1]
        except (SyntaxError, IndexError):
            raise ValueError(
                '`interface` must be an Interface object or in the format of ' + '"node_name:interface_name"'
            )

        resolved = None
        for node in self.client.nodes.list(simulation=simulation):
            if node.name == node_name:
                for intf in node.interfaces:
                    if intf.name == interface_name:
                        resolved = intf
                        break
        if not resolved:
            raise ValueError('Interface ' + interface + ' does not exist')
        return self.client.simulation_interfaces.list(original=resolved, simulation=simulation)[0]
