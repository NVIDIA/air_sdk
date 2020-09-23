"""
SimulationNode module
"""
from copy import deepcopy
from .exceptions import AirUnexpectedResponse

class SimulationNode:
    """ Representiation of an AIR SimulationNode object """
    def __init__(self, api, **kwargs):
        self.simulation_node_api = api
        self.url = kwargs.get('url', None)
        self.id = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        self.simulation = kwargs.get('simulation', None)
        self.original = kwargs.get('original', None)
        self.interfaces = kwargs.get('interfaces', [])
        self.console_port = kwargs.get('console_port', None)
        self.state = kwargs.get('state', None)
        self.worker = kwargs.get('worker', None)
        self.serial_port = kwargs.get('serial_port', None)
        self.console_username = kwargs.get('console_username', None)
        self.console_password = kwargs.get('console_password', None)
        self.console_url = kwargs.get('console_url', None)

    def update(self, **kwargs):
        """
        Updates the simulation_node with a given set of key/values using a PUT call

        Arguments:
        **kwargs [dict] - A dictionary providing values to update. The dictionary will be merged
                          into the SimulationNode's current values
        """
        data = deepcopy(self.__dict__)
        del data['simulation_node_api']
        data.update(kwargs)
        self.simulation_node_api.update_simulation_node(self.id, data)

class SimulationNodeApi:
    """ Wrapper for the SimulationNode API """
    def __init__(self, api):
        """
        Arguments:
        api (AirApi) - Instance of the AirApi client class.
                       We assume the client has been authorized.
        """
        self.api = api
        self.url = self.api.api_url + '/simulation-node/'

    def update_simulation_node(self, simulation_node_id, data):
        """
        Updates the simulation_node with a given set of key/values using a PUT call

        Arguments:
        data (dict) - A dictionary providing values to use as the PUT payload

        Raises:
        AirUnexpectedResponse - Raised if the API does not return a 200
        """
        url = self.url + simulation_node_id + '/'
        res = self.api.put(url, json=data)
        if res.status_code != 200:
            message = getattr(res, 'data', getattr(res, 'text', res.status_code))
            raise AirUnexpectedResponse(message=message, status_code=res.status_code)

    def get_simulation_nodes(self, **kwargs):
        url = self.url
        if kwargs:
            url += '?'
            for key, value in kwargs.items():
                url += f'&{key}={value}'
        return self.api.get(url)
