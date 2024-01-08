# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Organization module
"""

from . import util
from .air_model import AirModel
from .fleet import Fleet, FleetApi


class Organization(AirModel):
    """
    Manage an Organization

    ### delete
    Delete the organization. Once successful, the object should no longer be used and will raise
    [`AirDeletedObject`](/docs/exceptions) when referenced.

    Raises:
    [`AirUnexpectedResposne`](/docs/exceptions) - Delete failed

    ### json
    Returns a JSON string representation of the organization

    ### refresh
    Syncs the organization with all values returned by the API

    ### update
    Update the organization with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """

    ORG_MEMBER_ROLE = 'Organization Member'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._members_api_url = f'{self._api.url}{self.id}/members/'

    def __repr__(self):
        if self._deleted or not self.name:
            return super().__repr__()
        return f'<Organization {self.name} {self.id}>'

    def add_member(self, username: str, roles: list = None):
        """
        Add a new member to the organization

        Arguments:
            username (str): The email address of the user to add
            roles (list, optional): A list of roles to assign the user. Valid values are
                'Organization Admin' or 'Organization Member'. If no roles list is provided,
                'Organization Member' is used as the default role.

        Example:
        ```
        >>> organization.add_member('user1@nvidia.com')
        >>> organization.add_member('user2@nvidia.com', roles=['Organization Admin'])
        ```
        """
        _roles = roles
        if not _roles:
            _roles = [self.ORG_MEMBER_ROLE]
        self._api.client.post(self._members_api_url, json={'username': username, 'roles': _roles})
        self.refresh()

    def add_members(self, members: list):
        # pylint: disable=line-too-long
        """
        Add new members to the organization

        Arguments:
            members (list): List of organization membership dicts in the format of
                {'username': <email_address>, 'roles': [<role>]}.
                'roles' is optional and defaults to ['Organization Member']
                <role> can be a value of 'Organization Admin' or 'Organization Member'.

        Example:
        ```
        >>> organization.add_members([{'username': 'user1@nvidia.com', 'roles': ['Organization Admin']}, {'username': 'user2@nvidia.com'}])
        ```
        """  # pylint: enable=line-too-long
        for member in members:
            if not member.get('roles', []):
                member['roles'] = [self.ORG_MEMBER_ROLE]
        self._api.client.post(self._members_api_url, json=members)
        self.refresh()

    def remove_member(self, username: str, **kwargs):
        """
        Remove a member from the organization

        Arguments:
            username (str): The email address of the user to remove

        Example:
        ```
        >>> organization.remove_member('user1@nvidia.com')
        """
        self._api.client.delete(self._members_api_url, json={'username': username})
        if kwargs.get('_refresh_when_done', True):
            self.refresh()

    def remove_members(self, members: list):
        """
        Remove multiple members from the organization

        Arguments:
            members (list): Email addresses of the users to remove

        Example:
        ```
        >>> organization.remove_members(['user1@nvidia.com', 'user2@nvidia.com'])
        """
        for member in members:
            self.remove_member(member, _refresh_when_done=False)
        self.refresh()

    @util.required_kwargs(['name'])
    def create_fleet(self, **kwargs):
        # pylint: disable=line-too-long
        """
        Create a new fleet for this organization
        Arguments:
            name (str): Name of the fleet
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
        >>> air.organization.create_fleet(name='MyFleet', prefix='fd10:1:1::', prefix_length=48, gateway_ipv4='10.0.0.1', port_range='20000-40000', container_ipv4_network='172.16.0.0', container_prefix=16, labels=['label1', 'label2'])
        <Fleet MyFleet 3dadd54d-583c-432e-9383-a2b0b1d7f221>
        ```
        """  # pylint: enable=line-too-long
        url = FleetApi(self._api.client).url
        kwargs['organization'] = self.id
        res = self._api.client.post(url, json=kwargs)
        util.raise_if_invalid_response(res, status_code=201)
        return Fleet(self, **res.json())


class OrganizationApi:
    """High-level interface for the Organization API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/organization/'

    def get(self, organization_id, **kwargs):
        """
        Get an existing organization

        Arguments:
            organization_id (str): Organization ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Organization`](/docs/organization)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.organizations.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Organization NVIDIA 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{organization_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Organization(self, **res.json())

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing organizations

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
        >>> air.organizations.list()
        [<Organization NVIDIA c51b49b6-94a7-4c93-950c-e7fa4883591>, <Organization Customer 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """  # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Organization(self, **organization) for organization in res.json()]

    @util.required_kwargs(['name'])
    def create(self, **kwargs):
        # pylint: disable=line-too-long
        """
        Create a new organization

        Arguments:
            name (str): Organization name
            members (list, optional): List of organization membership dicts in the format of
                {'username': <email_address>, 'roles': [<role>]}.
                'roles' is optional and defaults to ['Organization Member']
                <role> can be a value of 'Organization Admin' or 'Organization Member'.
                If no member list is provided, the calling user's account will be set as the
                organization admin by default.
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        [`Organization`](/docs/organization)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.organizations.create(name='NVIDIA', members=[{'username': 'user1@nvidia.com', 'roles': ['Organization Admin']}, {'username': 'user2@nvidia.com'}])
        <Organization NVIDIA 01298e0c-4ef1-43ec-9675-93160eb29d9f>
        ```
        """  # pylint: enable=line-too-long
        res = self.client.post(self.url, json=kwargs)
        util.raise_if_invalid_response(res, status_code=201)
        return Organization(self, **res.json())
