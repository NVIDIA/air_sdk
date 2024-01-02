# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Account module
"""

from . import user_preference, util
from .air_model import AirModel


class Account(AirModel):
    """
    Manage an Account
    ### json
    Returns a JSON string representation of the account

    ### refresh
    Syncs the account with all values returned by the API
    """

    _deletable = False
    _updatable = False

    def __repr__(self):
        if self._deleted or not self.username:
            return super().__repr__()
        return f'<Account {self.username} {self.id}>'


class AccountApi:
    """High-level interface for the Account API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/account/'

    def get(self, account_id, **kwargs):
        """
        Get an existing account

        Arguments:
            account_id (str): Account ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Account`](/docs/account)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.accounts.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Account mrobertson@nvidia.com 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{account_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Account(self, **res.json())

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing accounts

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
        >>> air.accounts.list()
        [<Account mrobertson@nvidia.com c51b49b6-94a7-4c93-950c-e7fa4883591>, <Account nmitchell@nvidia.com 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """
        # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Account(self, **account) for account in res.json()]

    def preferences(self, **kwargs):
        """
        Returns your global account preferences

        Arguments:
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`UserPreference`](/docs/userpreference)

        Example:
        ```
        >>> air.accounts.preferences()
        {"show": true}
        ```
        """
        res = self.client.get(f'{self.url}preferences/', params=kwargs)
        util.raise_if_invalid_response(res)
        return user_preference.UserPreference(self, **res.json())
