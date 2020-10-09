"""
Simulation module
"""
from copy import deepcopy
from .exceptions import AirUnexpectedResponse
from .util import raise_if_invalid_response

class Simulation:
    """ Representiation of an AIR Simulation object """
    def __init__(self, api, **kwargs):
        self.simulation_api = api
        self.url = kwargs.get('url', None)
        self.id = kwargs.get('id', None)
        self.topology = kwargs.get('topology', None)
        self.nodes = kwargs.get('nodes', [])
        self.services = kwargs.get('services', [])
        self.name = kwargs.get('name', None)
        self.expires = kwargs.get('expires', False)
        self.expires_at = kwargs.get('expires_at', None)
        self.sleep = kwargs.get('sleep', False)
        self.sleep_at = kwargs.get('sleep_at', None)
        self.netq_username = kwargs.get('netq_username', None)
        self.netq_password = kwargs.get('netq_password', None)

    def update(self, **kwargs):
        """
        Updates the simulation with a given set of key/values using a PUT call

        Arguments:
        **kwargs [dict] - A dictionary providing values to update. The dictionary will be merged
                          into the simulation's current values
        """
        data = deepcopy(self.__dict__)
        del data['simulation_api']
        data.update(kwargs)
        self.simulation_api.update_simulation(self.id, data)

    def create_service(self, name, interface, dest_port, **kwargs):
        """
        Create a new service for this simulation

        Arguments:
        name (str) - Name of the service
        interface (str) - Interface that the service should be created for. Specify this in the
                           format of 'node_name:interface_name' (ex: 'oob-mgmt-server:eth0')
        dest_port (int) - Port number
        **kwargs [dict] - Optional key/values to include with the POST call

        Raises:
        ValueError - Raised if the interface is invalid or not found
        """
        self.simulation_api.api.service.create_service(self.id, name, interface, dest_port,
                                                       **kwargs)

    def add_permission(self, email, **kwargs):
        """
        Adds permission for a given user to this simulation

        Arguments:
        email (str) - Email address of the user being given permission
        kwargs (dict) - Additional key/value pairs to be passed in the POST request.
                        The caller MUST pass either `topology` or `simulation`

        Raises:
        AirUnexpectedResponse - Raised if the API returns any unexpected response
        """
        self.simulation_api.api.permission.create_permission(email, simulation=self.id, **kwargs)

    def start(self):
        """ Starts a simulation with a call to the /simulation/:id/control API """
        self.simulation_api.control(self.id, 'load')

    def store(self):
        """ Stores a simulation with a call to the /simulation/:id/control API """
        self.simulation_api.control(self.id, 'store')

    def delete(self):
        """ Deletes a simulation with a call to the /simulation/:id/control API """
        self.simulation_api.control(self.id, 'destroy')

class SimulationApi:
    """ Wrapper for the Simulation API """
    def __init__(self, api):
        """
        Arguments:
        api (AirApi) - Instance of the AirApi client class.
                       We assume the client has been authorized.
        """
        self.api = api
        self.url = self.api.api_url + '/simulation/'

    def get_simulations(self):
        """ Returns a list of active simulations """
        res = self.api.get(self.url)
        return res.json()

    def get_simulation(self):
        """ TODO """

    def create_simulation(self, **kwargs):
        """
        Create a new simulation.

        Arguments:
        kwargs (dict) - Arguments passed to the Simulation create API

        Returns:
        Simulation - Newly created simulation object
        dict - JSON response from the API

        Raises:
        AirUnexpectedResponse - Raised if an unexpected response is received from the API
        """
        res = self.api.post(self.url, json=kwargs)
        if res.status_code != 201:
            message = getattr(res, 'data', getattr(res, 'text', res.status_code))
            raise AirUnexpectedResponse(message=message, status_code=res.status_code)
        simulation = Simulation(self, **res.json())
        return simulation, res.json()

    def update_simulation(self, simulation_id, data):
        """
        Updates the simulation with a given set of key/values using a PUT call

        Arguments:
        data (dict) - A dictionary providing values to use as the PUT payload

        Raises:
        AirUnexpectedResponse - Raised if the API does not return a 200
        """
        url = self.url + simulation_id + '/'
        res = self.api.put(url, json=data)
        if res.status_code != 200:
            message = getattr(res, 'data', getattr(res, 'text', res.status_code))
            raise AirUnexpectedResponse(message=message, status_code=res.status_code)

    def duplicate(self, snapshot_id, **kwargs):
        """
        Arguments:
        snapshot_id (str) - UUID of the snapshot simulation to be duplicated
        kwargs [dict] - Options to include in the /control API call

        Returns:
        Simulation - Python representation of the newly created simulation object
        dict - JSON response from the API

        Raises:
        AirUnexpectedResponse - Raised if the API returns a non-200 or an invalid JSON response
        """
        url = self.url + snapshot_id + '/control/'
        data = kwargs
        data['action'] = 'duplicate'
        res = self.api.post(url, json=data)
        raise_if_invalid_response(res)
        payload = res.json()
        if payload.get('simulation', None):
            sim = Simulation(self, **payload['simulation'])
            return sim, payload
        raise AirUnexpectedResponse(payload)

    def control(self, simulation_id, action, **kwargs):
        """
        Calls the POST /simulation/:id/control/ API to control a simulation

        Arguments:
        simulation_id (str) - UUID of the simulation to control
        action (str) - Action to perform
        kwargs [dict] - Optional key/value pairs to include in the POST payload

        Returns:
        HTTPResponse
        """
        url = self.url + simulation_id + '/control/'
        data = deepcopy(kwargs)
        data['action'] = action
        return self.api.post(url, json=data)
