"""
Capacity module
"""

class Capacity:
    """ Representation of an AIR Capacity object """
    def __init__(self, api, **kwargs):
        self.capacity_api = api
        self.copies = kwargs.get('copies')

class CapacityApi:
    """ Wrapper for the /capacity API """
    def __init__(self, api):
        self.api = api
        self.url = self.api.api_url + '/capacity/'

    def get_capacity(self, simulation=None, simulation_id=None):
        """
        Gets a Capacity object for the given simulation

        Arguments:
        simulation [Simulation]
        simulation_id [str|uuid]

        Returns:
        Capacity
        """
        if not simulation and not simulation_id:
            raise ValueError('Must pass a simulation or simulation_id argument')
        sim_id = simulation_id
        if simulation:
            sim_id = simulation.id
        res = self.api.get(self.url + str(sim_id))
        return Capacity(self, **res.json())
