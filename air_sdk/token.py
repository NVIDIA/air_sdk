# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Token module
"""

from . import util
from .air_model import AirModel


class Token(AirModel):
    """
    View an API Token

    ### json
    Returns a JSON string representation of the interface

    ### refresh
    Syncs the interface with all values returned by the API
    """

    # _deletable = False
    _updatable = False

    def __repr__(self):
        if self._deleted or not self.name:
            return super().__repr__()
        if hasattr(self, 'id'):
            return f'<Token {self.name} {self.id}>'
        if hasattr(self, 'token'):
            return f'<Token {self.name} {self.token}>'
        return f'<Token {self.name}>'


class TokenApi:
    """High-level interface for the Token API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/api-token/'

    def delete(self, token_id, **kwargs):
        """
        Deletes an api token

        Arguments:
            token_id (str): Token ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters


        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 204 No Content
            or valid response JSON

        Example:
        ```
        >>> air.api_tokens.delete('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        ```
        """
        url = f'{self.url}{token_id}/'
        res = self.client.delete(url, params=kwargs)
        util.raise_if_invalid_response(res, status_code=204, data_type=None)

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing tokens

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
        >>> air.tokens.list()
        [<Interface eth0 c51b49b6-94a7-4c93-950c-e7fa4883591>, <Interface eth1 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """
        # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Token(self, **token) for token in res.json()]

    @util.required_kwargs(['name'])
    def create(self, **kwargs):
        """
        Add a new api token to your account

        Arguments:
            name (str): Descriptive name for the api token
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        [`api-token`](/docs/api-token)

        Raises:
        [`AirUnexpectedResponse`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.api_tokens.create(name='my_api_token')
        <Token my_api_token 01298e0c-4ef1-43ec-9675-93160eb29d9f>
        ```
        """
        res = self.client.post(self.url, json=kwargs)
        util.raise_if_invalid_response(res, status_code=201)
        return Token(self, **res.json())
