# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
SSH Key module
"""

from . import util
from .air_model import AirModel


class SSHKey(AirModel):
    """
    Manage a SSH Key

    ### delete
    Delete the key. Once successful, the object should no longer be used and will raise
    [`AirDeletedObject`](/docs/exceptions) when referenced.

    Raises:
    [`AirUnexpectedResposne`](/docs/exceptions) - Delete failed

    ### json
    Returns a JSON string representation of the key

    ### refresh
    Syncs the key with all values returned by the API
    """

    _updatable = False

    def __repr__(self):
        if self._deleted or not self.name:
            return super().__repr__()
        return f'<SSHKey {self.name} {self.id}>'


class SSHKeyApi:
    """High-level interface for the SSHKey API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/sshkey/'

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing keys

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
        >>> air.ssh_keys.list()
        [<SSHKey mykey c51b49b6-94a7-4c93-950c-e7fa4883591>, <SSHKey test_key 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """  # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [SSHKey(self, **key) for key in res.json()]

    @util.required_kwargs(['public_key', 'name'])
    def create(self, **kwargs):
        """
        Add a new public key to your account

        Arguments:
            name (str): Descriptive name for the public key
            public_key (str): Public key
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        [`SSHKey`](/docs/sshkey)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.ssh_keys.create(name='my_pub_key', public_key='<key_string>')
        <SSHKey my_pub_key 01298e0c-4ef1-43ec-9675-93160eb29d9f>
        ```
        """
        res = self.client.post(self.url, json=kwargs)
        util.raise_if_invalid_response(res, status_code=201)
        return SSHKey(self, **res.json())
