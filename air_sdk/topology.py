"""
Topology module
"""
from copy import deepcopy
from .exceptions import AirUnexpectedResponse

class Topology:
    """ Representiation of an AIR Topology object """
    def __init__(self, api, **kwargs):
        self.topology_api = api
        self.url = kwargs.get('url', None)
        self.id = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        self.organization = kwargs.get('organization', None)
        self.documentation = kwargs.get('documentation', None)
        self.diagram_url = kwargs.get('diagram_url', None)

    def update(self, **kwargs):
        """
        Updates the topology with a given set of key/values using a PUT call

        Arguments:
        **kwargs [dict] - A dictionary providing values to update. The dictionary will be merged
                          into the topology's current values
        """
        data = deepcopy(self.__dict__)
        del data['topology_api']
        data.update(kwargs)
        self.topology_api.update_topology(self.id, data)

    def add_permission(self, email, **kwargs):
        """
        Adds permission for a given user to this topology

        Arguments:
        email (str) - Email address of the user being given permission
        kwargs (dict) - Additional key/value pairs to be passed in the POST request.
                        The caller MUST pass either `topology` or `simulation`

        Raises:
        AirUnexpectedResponse - Raised if the API returns any unexpected response
        """
        self.topology_api.api.permission.create_permission(email, topology=self.id, **kwargs)

class TopologyApi:
    """ Wrapper for the Topology API """
    def __init__(self, api):
        """
        Arguments:
        api (AirApi) - Instance of the AirApi client class.
                       We assume the client has been authorized.
        """
        self.api = api
        self.url = self.api.api_url + '/topology/'

    def get_topologies(self):
        """ Returns a list of topologies """
        res = self.api.get(self.url)
        return res.json()

    def get_topology(self):
        """ TODO """

    def create_topology(self, json=None, dot=None):
        """
        Create a new topology. The caller MUST either pass a `json` or `dot` argument.

        Arguments:
        json [dict] - JSON-based topology definition
        dot [str] - DOT-based topology definition

        Returns:
        Topology - Newly created topology object
        dict - JSON response from the API

        Raises:
        AirUnexpectedResponse - Raised if an unexpected response is received from the API
        """
        if not json and not dot:
            raise ValueError('TopologyApi.create_topology requires a `json` or `dot` argument')
        if json:
            res = self.api.post(self.url, json=json)
        elif dot:
            res = self.api.post(self.url, data=dot, headers={'Content-type': 'text/vnd.graphviz'})
        if res.status_code != 201:
            message = getattr(res, 'data', getattr(res, 'text', res.status_code))
            raise AirUnexpectedResponse(message=message, status_code=res.status_code)
        topology = Topology(self, **res.json())
        return topology, res.json()

    def update_topology(self, topology_id, data):
        """
        Updates the topology with a given set of key/values using a PUT call

        Arguments:
        data (dict) - A dictionary providing values to use as the PUT payload

        Raises:
        AirUnexpectedResponse - Raised if the API does not return a 200
        """
        url = self.url + topology_id + '/'
        res = self.api.put(url, json=data)
        if res.status_code != 200:
            message = getattr(res, 'data', getattr(res, 'text', res.status_code))
            raise AirUnexpectedResponse(message=message, status_code=res.status_code)
