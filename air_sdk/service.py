"""
Service module
"""
from .exceptions import AirUnexpectedResponse
from .util import raise_if_invalid_response

class Service:
    """ Representiation of an AIR Service object """
    def __init__(self, api, **kwargs):
        self.service_api = api
        self.url = kwargs.get('url', None)
        self.id = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        self.simulation = kwargs.get('simulation', None)
        self.interface = kwargs.get('interface', None)
        self.dest_port = kwargs.get('dest_port', None)
        self.src_port = kwargs.get('src_port', None)
        self.link = kwargs.get('link', None)

class ServiceApi:
    """ Wrapper for the Service API """
    def __init__(self, api):
        """
        Arguments:
        api (AirApi) - Instance of the AirApi client class.
                       We assume the client has been authorized.
        """
        self.api = api
        self.url = self.api.api_url + '/service/'

    def get_services(self):
        """ Returns a list of services """
        res = self.api.get(self.url)
        return res.json()

    def get_service(self, service_id):
        """
        Get an instance of a service

        Arguments:
        service_id (str) - Service ID

        Returns
        Service
        """
        res = self.api.get(f'{self.url}{service_id}/')
        service = Service(self, **res.json())
        return service

    def create_service(self, simulation_id, name, interface, dest_port, **kwargs):
        """
        Create a new service

        Arguments:
        simulation_id (str) - UUID of the simulation to attach the service to
        name (str) - Name of the service
        interface (str) - Interface that the service should be created for. Specify this in the
                           format of 'node_name:interface_name' (ex: 'oob-mgmt-server:eth0')
        dest_port (int) - Port number
        **kwargs [dict] - Optional key/values to include with the POST call

        Returns:
        Service - Newly created service object
        dict - JSON response from the API

        Raises:
        ValueError - Raised if the interface is invalid or not found
        AirUnexpectedResponse - Raised if an unexpected response is received from the API
        """
        try:
            node_name = interface.split(':')[0]
            interface_name = interface.split(':')[1]
        except (SyntaxError, IndexError):
            raise ValueError('`interface` must be in the format of "node_name:interface_name"')
        data = kwargs
        data['simulation'] = simulation_id
        data['name'] = name
        data['dest_port'] = dest_port

        interface_id = ''
        for node in self.api.node.get_nodes(simulation_id):
            if node['name'] == node_name:
                for intf in node['interfaces']:
                    if intf['name'] == interface_name:
                        interface_id = intf['id']

        if not interface_id:
            raise ValueError('Interface ' + interface + ' does not exist')

        sim_ints = self.api.simulation_interface.get_simulation_interfaces(simulation_id,
                                                                           interface_id)
        try:
            interface_id = sim_ints[0]['id']
        except (IndexError, KeyError):
            raise AirUnexpectedResponse(sim_ints)

        data['interface'] = interface_id

        res = self.api.post(self.url, json=data)
        raise_if_invalid_response(res, 201)
        service = Service(self, **res.json())
        return service, res.json()
