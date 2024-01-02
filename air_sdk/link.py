# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Link module
"""

from . import util
from .air_model import AirModel


class Link(AirModel):
    """
    Manage a Link

    ### delete
    Delete the link. Once successful, the object should no longer be used and will raise
    [`AirDeletedObject`](/docs/exceptions) when referenced.

    Raises:
    [`AirUnexpectedResposne`](/docs/exceptions) - Delete failed

    ### json
    Returns a JSON string representation of the link

    ### refresh
    Syncs the link with all values returned by the API

    ### update
    Update the link with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """

    def __repr__(self):
        if self._deleted:
            return super().__repr__()
        return f'<Link {self.id}>'


class LinkApi:
    """High-level interface for the Link API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/link/'

    def get(self, link_id, **kwargs):
        """
        Get an existing link

        Arguments:
            link_id (str): Link ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Link`](/docs/link)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.links.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Link 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{link_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Link(self, **res.json())

    def list(self, **kwargs):
        """
        List existing links

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
        >>> air.links.list()
        [<Link c51b49b6-94a7-4c93-950c-e7fa4883591>, <Link 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Link(self, **link) for link in res.json()]

    @util.required_kwargs(['topology', 'interfaces'])
    def create(self, **kwargs):
        # pylint: disable=line-too-long
        """
        Create a new link

        Arguments:
            topology (str | `Topology`): `Topology` or ID
            interfaces (list): List of `Interface` objects or IDs
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        [`Link`](/docs/link)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.links.create(topology=topology, interfaces=[intf1, 'fd61e3d8-af2f-4735-8b1d-356ee6bf4abe'])
        <Link 01298e0c-4ef1-43ec-9675-93160eb29d9f>
        ```
        """  # pylint: enable=line-too-long
        res = self.client.post(self.url, json=kwargs)
        util.raise_if_invalid_response(res, status_code=201)
        return Link(self, **res.json())
