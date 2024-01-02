# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Job module
"""

from . import util
from .air_model import AirModel


class Job(AirModel):
    """
    Manage a Job

    ### json
    Returns a JSON string representation of the job

    ### refresh
    Syncs the job with all values returned by the API

    ### update
    Update the job with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """

    _deletable = False

    def __repr__(self):
        if self._deleted or not self.category:
            return super().__repr__()
        return f'<Job {self.category} {self.id}>'


class JobApi:
    """High-level interface for the Job API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/job/'

    def get(self, job_id, **kwargs):
        """
        Get an existing job

        Arguments:
            job_id (str): Job ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Job`](/docs/job)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.jobs.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Job START 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{job_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Job(self, **res.json())

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing jobs

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
        >>> air.jobs.list()
        [<Job START c51b49b6-94a7-4c93-950c-e7fa4883591>, <Job STOP 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """  # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Job(self, **job) for job in res.json()]
