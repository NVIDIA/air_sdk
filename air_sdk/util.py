"""
Helper utils
"""

from json import JSONDecodeError
from .exceptions import AirUnexpectedResponse

def raise_if_invalid_response(res, status_code=200):
    """
    Validates that a given API response has the expected status code and JSON payload

    Arguments:
    res (requests.HTTPResponse) - API response object
    status_code [int] - Expected status code (default: 200)

    Raises:
    AirUnexpectedResponse - Raised if an unexpected response is received from the API
    """
    if res.status_code != status_code:
        raise AirUnexpectedResponse(res.status_code)
    try:
        res.json()
    except JSONDecodeError:
        raise AirUnexpectedResponse(res)
