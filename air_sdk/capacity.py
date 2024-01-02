# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Capacity module
"""

from . import util
from .air_model import AirModel


class Capacity(AirModel):
    """
    View platform capacity

    ### json
    Returns a JSON string representation of the capacity

    ### refresh
    Syncs the capacity with all values returned by the API
    """

    _deletable = False
    _updatable = False

    def __repr__(self):
        if self._deleted or not self.copies:
            return super().__repr__()
        return f'<Capacity {self.copies}>'


class CapacityApi:
    """High-level interface for the Simulation API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/capacity/'

    @util.deprecated('CapacityApi.get()')
    def get_capacity(self, simulation=None, simulation_id=None):  # pylint: disable=missing-function-docstring
        if not simulation and not simulation_id:
            raise ValueError('Must pass a simulation or simulation_id argument')
        sim_id = simulation_id or simulation.id
        return self.get(simulation_id=sim_id)

    def get(self, simulation_id, **kwargs):
        """
        Get current platform capacity for a [`Simulation`](/docs/simulation)

        Arguments:
            simulation_id (str | `Simulation`): Simulation or ID

        Returns:
        [`Capacity`](/docs/capacity)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.capacity.get(simulation)
        <Capacity 30>
        ```
        """
        if isinstance(simulation_id, AirModel):
            simulation_id = simulation_id.id
        url = f'{self.url}{simulation_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Capacity(self, **res.json())
