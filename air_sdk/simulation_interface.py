"""
SimulationInterface module
"""

class SimulationInterface:
    """ Representiation of an AIR SimulationInterface object """
    def __init__(self, api, **kwargs):
        self.simulation_interface_api = api
        self.id = kwargs.get('id', None)
        self.url = kwargs.get('url', None)
        self.node = kwargs.get('node', None)
        self.original = kwargs.get('original', None)
        self.link_up = kwargs.get('link_up', False)
        self.services = kwargs.get('services', [])
        self.internal_ipv4 = kwargs.get('internal_ipv4', None)
        self.prefix_ipv6 = kwargs.get('prefix_ipv6', None)
        self.full_ipv6 = kwargs.get('full_ipv6', None)
        self.mac_address = kwargs.get('mac_address', None)

class SimulationInterfaceApi:
    """ Wrapper for the SimulationInterface API """
    def __init__(self, api):
        """
        Arguments:
        api (AirApi) - Instance of the AirApi client class.
                       We assume the client has been authorized.
        """
        self.api = api
        self.url = self.api.api_url + '/simulation-interface/'

    def get_simulation_interfaces(self, simulation_id='', original_id=''):
        """
        Get a list of active simulation interface

        Arguments:
        simulation_id [str] - Filter by simulation
        original_id [str] - Filter by interface
        """
        url = self.url + '?'
        param_list = []
        if simulation_id:
            param_list.append('simulation=' + simulation_id)
        if original_id:
            param_list.append('original=' + original_id)
        if param_list:
            params = '&'.join(param_list)
            url += params
        res = self.api.get(url)
        return res.json()
