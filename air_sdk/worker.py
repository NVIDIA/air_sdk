# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Worker module
"""

from . import util
from .air_model import AirModel

class Worker(AirModel):
    """
    Manage a Worker

    ### json
    Returns a JSON string representation of the worker

    ### refresh
    Syncs the worker with all values returned by the API

    ### update
    Update the worker with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """
    _deletable = False

    def __repr__(self):
        if self._deleted or not self.fqdn:
            return super().__repr__()
        return f'<Worker {self.fqdn} {self.id}>'

    @util.deprecated('<worker_instance>.available')
    def set_available(self, available):
        """
        Sets a worker's `available` value in AIR

        Arguments:
        available (bool)
        """
        self.available = available #pylint: disable=attribute-defined-outside-init

class WorkerApi:
    """ High-level interface for the Worker API """
    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/worker/'

    @util.deprecated('WorkerApi.list()')
    def get_workers(self, **kwargs): #pylint: disable=missing-function-docstring
        return self.list(**kwargs)

    @util.deprecated('Worker.update()')
    def update_worker(self, worker_id, **kwargs): #pylint: disable=missing-function-docstring
        worker = self.get(worker_id)
        return worker.update(**kwargs)

    def get(self, worker_id, **kwargs):
        """
        Get an existing worker

        Arguments:
            worker_id (str): Worker ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Worker`](/docs/worker)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.workers.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Worker worker01 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{worker_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Worker(self, **res.json())

    def list(self, **kwargs):
        #pylint: disable=line-too-long
        """
        List existing workers

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
        >>> air.workers.list()
        [<Worker worker01 c51b49b6-94a7-4c93-950c-e7fa4883591>, <Worker worker02 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """ #pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Worker(self, **worker) for worker in res.json()]

    @util.required_kwargs(['cpu', 'memory', 'storage', 'ip_address', 'port_range', 'username',
                           'password'])
    def create(self, **kwargs):
        #pylint: disable=line-too-long
        """
        Create a new worker

        Arguments:
            cpu (int): Number of vCPUs the worker can support
            memory (int): Amount of memory (in MB) a worker can support
            storage (int): Amount of storage (in GB) a worker can support
            ip_address (str): Internal IP address
            port_range (str): Range of ports available on the worker
            username (str): Worker username for API access
            password (str): Worker password for API access
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        [`Worker`](/docs/worker)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.workers.create(cpu=100, memory=200000, storage=1000, ip_address='10.1.1.1', port_range='10000-30000', username='worker01', password='secret')
        <Worker my_sim 01298e0c-4ef1-43ec-9675-93160eb29d9f>
        ```
        """ #pylint: enable=line-too-long
        res = self.client.post(self.url, json=kwargs)
        util.raise_if_invalid_response(res, status_code=201)
        return Worker(self, **res.json())
