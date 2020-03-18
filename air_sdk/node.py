"""
Node module
"""

class Node:
    """ Representiation of an AIR Node object """
    def __init__(self, api, **kwargs):
        self.node_api = api
        self.url = kwargs.get('url', None)
        self.id = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        self.os = kwargs.get('os', None)
        self.memory = kwargs.get('memory', None)
        self.storage = kwargs.get('storage', None)
        self.cpu = kwargs.get('cpu', None)
        self.interfaces = kwargs.get('interfaces', [])
        self.topology = kwargs.get('topology', None)

class NodeApi:
    """ Wrapper for the Node API """
    def __init__(self, api):
        """
        Arguments:
        api (AirApi) - Instance of the AirApi client class.
                       We assume the client has been authorized.
        """
        self.api = api
        self.url = self.api.api_url + '/node/'

    def get_nodes(self, simulation_id=''):
        """
        Returns a list of nodes

        Arguments:
        simulation_id [str] - Filter the results for a given simulation
        """
        url = self.url
        if simulation_id:
            url += '?simulation=' + simulation_id
        res = self.api.get(url)
        return res.json()

    def get_node(self):
        """ TODO """
