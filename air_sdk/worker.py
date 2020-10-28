"""
Worker module
"""
from copy import deepcopy

from .exceptions import AirUnexpectedResponse

class Worker:
    """ Representation of an AIR Worker object """
    def __init__(self, api, **kwargs):
        self.worker_api = api
        self.url = kwargs.get('url')
        self.id = kwargs.get('id')
        self.cpu = kwargs.get('cpu')
        self.memory = kwargs.get('memory')
        self.storage = kwargs.get('storage')
        self.ip_address = kwargs.get('ip_address')
        self.port_range = kwargs.get('port_range')
        self.region = kwargs.get('region')
        self.available = kwargs.get('available')
        self.fqdn = kwargs.get('fqdn')

    def set_available(self, available):
        """
        Sets a worker's `available` value in AIR

        Arguments:
        available (bool)
        """
        self.available = available
        data = deepcopy(self.__dict__)
        del data['worker_api']
        self.worker_api.update_worker(self.id, **data)

class WorkerApi:
    """ Wrapper for the /worker API """
    def __init__(self, api):
        self.api = api
        self.url = self.api.api_url + '/worker/'

    def get_workers(self, **kwargs):
        """
        List workers

        Arguments:
        kwargs [dict] - Optional query parameters to include with the GET request

        Returns:
        list - List of Worker objects
        """
        url = self.url + '?'
        for key, val in kwargs.items():
            url += f'&{key}={val}'
        res = self.api.get(url)
        workers = []
        for worker in res.json():
            workers.append(Worker(self, **worker))
        return workers

    def update_worker(self, worker_id, **kwargs):
        """
        Update a worker record via a PUT call

        Arguments:
        worker_id (str|uuid) - Worker UUID
        kwargs [dict] - Key/value pairs to include in the request payload
        """
        url = f'{self.url}{worker_id}/'
        payload = kwargs
        payload['id'] = str(worker_id)
        res = self.api.put(url, json=payload)
        if res.status_code != 200:
            raise AirUnexpectedResponse(res.text, res.status_code)
        return Worker(self, **res.json())
