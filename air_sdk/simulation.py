"""
Simulation module
"""

class Simulation:
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
