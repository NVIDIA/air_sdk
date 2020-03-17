"""
Permission module
"""
from .util import raise_if_invalid_response

class Permission:
    """ Representiation of an AIR Permission object """
    def __init__(self, api, **kwargs):
        self.permission_api = api
        self.id = kwargs.get('id', None)
        self.url = kwargs.get('url', None)
        self.email = kwargs.get('email', None)
        self.account = kwargs.get('account', None)
        self.topology = kwargs.get('topology', None)
        self.simulation = kwargs.get('simulation', None)
        self.write_ok = kwargs.get('write_ok', False)

class PermissionApi:
    """ Wrapper for the Permission API """
    def __init__(self, api):
        """
        Arguments:
        api (AirApi) - Instance of the AirApi client class.
                       We assume the client has been authorized.
        """
        self.api = api
        self.url = self.api.api_url + '/permission/'

    def create_permission(self, email, **kwargs):
        """
        Creates a permission

        Arguments:
        email (str) - Email address of the user being given permission
        kwargs (dict) - Additional key/value pairs to be passed in the POST request.
                        The caller MUST pass either `topology` or `simulation`

        Returns:
        Permission - Newly created permission object
        dict - JSON response from the API

        Raises:
        AirUnexpectedResponse - Raised if the API returns any unexpected response
        """
        if not kwargs.get('topology') and not kwargs.get('simulation', None):
            raise ValueError('Creating a permission requires either a `simulation` or ' + \
                             '`topology` argument')
        data = kwargs
        data['email'] = email
        res = self.api.post(self.url, data)
        raise_if_invalid_response(res, 201)
        payload = res.json()
        permission = Permission(self, **payload)
        return permission, payload
