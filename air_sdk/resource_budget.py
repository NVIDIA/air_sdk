# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
ResourceBudget module
"""

from . import util
from .air_model import AirModel


class ResourceBudget(AirModel):
    """
    Manage a ResourceBudget

    ### json
    Returns a JSON string representation of the budget

    ### refresh
    Syncs the budget with all values returned by the API

    ### update
    Update the budget with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """

    _deletable = False

    def __repr__(self):
        if self._deleted:
            return super().__repr__()
        return f'<ResourceBudget {self.id}>'


class ResourceBudgetApi:
    """High-level interface for the ResourceBudget API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/resource-budget/'

    def get(self, budget_id, **kwargs):
        """
        Get an existing budget

        Arguments:
            budget_id (str): ResourceBudget ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`ResourceBudget`](/docs/resourcebudget)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.resource_budgets.get('c604c262-396a-48a0-a8f6-31708c0cff82')
        <ResourceBudget c604c262-396a-48a0-a8f6-31708c0cff82>
        ```
        """
        url = f'{self.url}{budget_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return ResourceBudget(self, **res.json())

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing budgets

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
        >>> air.resource_budgets.list()
        [<ResourceBudget c604c262-396a-48a0-a8f6-31708c0cff82>, <ResourceBudget 906675f7-8b8d-4f52-b59d-52847af2f0ef>]
        ```
        """  # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [ResourceBudget(self, **budget) for budget in res.json()]
