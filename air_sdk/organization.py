"""
Organization module
"""

from . import util
from .air_model import AirModel

class Organization(AirModel):
    """
    Manage an Organization

    ### delete
    Delete the organization. Once successful, the object should no longer be used and will raise
    [`AirDeletedObject`](/docs/exceptions) when referenced.

    Raises:
    [`AirUnexpectedResposne`](/docs/exceptions) - Delete failed

    ### json
    Returns a JSON string representation of the organization

    ### refresh
    Syncs the organization with all values returned by the API

    ### update
    Update the organization with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """
    def __repr__(self):
        if self._deleted or not self.name:
            return super().__repr__()
        return f'<Organization {self.name} {self.id}>'
class OrganizationApi:
    """ High-level interface for the Organization API """
    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/organization/'

    def get(self, organization_id, **kwargs):
        """
        Get an existing organization

        Arguments:
            organization_id (str): Organization ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Organization`](/docs/organization)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.organizations.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Organization NVIDIA 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{organization_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Organization(self, **res.json())

    def list(self, **kwargs):
        #pylint: disable=line-too-long
        """
        List existing organizations

        Arguments:
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        list

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.organizations.list()
        [<Organization NVIDIA c51b49b6-94a7-4c93-950c-e7fa4883591>, <Organization Customer 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """ #pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Organization(self, **organization) for organization in res.json()]

    @util.required_kwargs(['name', 'members'])
    def create(self, **kwargs):
        #pylint: disable=line-too-long
        """
        Create a new organization

        Arguments:
            name (str): Organization name
            members (list): List of member [`Account`](/docs/account) objects or IDs
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        [`Organization`](/docs/organization)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.organizations.create(name='NVIDIA', members=[account, 'fa42f2ce-8494-4d4d-87fd-d9ebc18831bd'])
        <Organization NVIDIA 01298e0c-4ef1-43ec-9675-93160eb29d9f>
        ```
        """ #pylint: enable=line-too-long
        res = self.client.post(self.url, json=kwargs)
        util.raise_if_invalid_response(res, status_code=201)
        return Organization(self, **res.json())
