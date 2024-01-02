# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Permission module
"""

from . import util
from .air_model import AirModel


class Permission(AirModel):
    """
    Manage a Permission

    ### delete
    Delete the permission. Once successful, the object should no longer be used and will raise
    [`AirDeletedObject`](/docs/exceptions) when referenced.

    Raises:
    [`AirUnexpectedResposne`](/docs/exceptions) - Delete failed

    ### json
    Returns a JSON string representation of the permission

    ### refresh
    Syncs the permission with all values returned by the API

    ### update
    Update the permission with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """

    _updatable = False

    def __repr__(self):
        if self._deleted:
            return super().__repr__()
        return f'<Permission {self.id}>'


class PermissionApi:
    """High-level interface for the Permission API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/permission/'

    @util.deprecated('PermissionApi.create()')
    def create_permission(self, email, **kwargs):  # pylint: disable=missing-function-docstring
        kwargs['email'] = email
        return self.create(**kwargs)

    @util.required_kwargs([('topology', 'simulation', 'subject_id'), 'email'])
    def create(self, **kwargs):
        """
        Create a new permission. The caller MUST provide `simulation`, `topology`, or `subject_id`

        Arguments:
            email (str): Email address for the user being granted permission
            simulation (str | `Simulation`, optional): `Simulation` or ID
            topology (str | `Topology`, optional): `Topology` or ID
            subject_id (str | `AirModel`, optional): `AirModel` instance or ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Permission`](/docs/permission)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.permissions.create(email='mrobertson@nvidia.com', topology=topology, write_ok=True)
        <Permission 01298e0c-4ef1-43ec-9675-93160eb29d9f>
        >>> air.permissions.create(email='mrobertson@nvidia.com',
        ... subject_id='80cf922a-7b80-4795-8cc5-550833ab1cec', subject_model='simulation.image')
        <Permission 8a09ea66-51f9-4ddd-8416-62c266cd959e>
        ```
        """
        res = self.client.post(self.url, json=kwargs)
        util.raise_if_invalid_response(res, status_code=201)
        return Permission(self, **res.json())

    def get(self, permission_id, **kwargs):
        """
        Get an existing permission

        Arguments:
            permission_id (str): Permission ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Permission`](/docs/permission)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.permissions.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Permission 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{permission_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Permission(self, **res.json())

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing permissions

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
        >>> air.permissions.list()
        [<Permission c51b49b6-94a7-4c93-950c-e7fa4883591>, <Permission 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """  # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Permission(self, **permission) for permission in res.json()]
