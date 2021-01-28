"""
Helper utils
"""

import logging
from json import JSONDecodeError

from .exceptions import AirUnexpectedResponse

def raise_if_invalid_response(res, status_code=200, data_type=dict):
    """
    Validates that a given API response has the expected status code and JSON payload

    Arguments:
    res (requests.HTTPResponse) - API response object
    status_code [int] - Expected status code (default: 200)

    Raises:
    AirUnexpectedResponse - Raised if an unexpected response is received from the API
    """
    json = None
    if res.status_code != status_code:
        logging.debug(res.text)
        raise AirUnexpectedResponse(message=res.text, status_code=res.status_code)
    if not data_type:
        return
    try:
        json = res.json()
    except JSONDecodeError:
        raise AirUnexpectedResponse(message=res.text, status_code=res.status_code)
    if not isinstance(json, data_type):
        raise AirUnexpectedResponse(message=f'Expected API response to be of type {data_type}, ' + \
                                            f'got {type(json)}',
                                    status_code=res.status_code)

def required_kwargs(required):
    """ Decorator to enforce required kwargs for a function """
    if not isinstance(required, list):
        required = [required]
    def wrapper(method):
        def wrapped(*args, **kwargs):
            for arg in required:
                if isinstance(arg, tuple):
                    present = False
                    for option in arg:
                        if option in kwargs:
                            present = True
                            break
                    if not present:
                        raise AttributeError(f'{method} requires one of the following: {arg}')
                else:
                    if arg not in kwargs:
                        raise AttributeError(f'{method} requires {arg}')
            return method(*args, **kwargs)
        return wrapped
    return wrapper

def deprecated(new=None):
    """ Decorator to log a warning when calling a deprecated function """
    def wrapper(method):
        def wrapped(*args, **kwargs):
            msg = f'{method} has been deprecated and will be removed in a future release.'
            if new:
                msg += f' Use {new} instead.'
            logging.warning(msg)
            return method(*args, **kwargs)
        return wrapped
    return wrapper
