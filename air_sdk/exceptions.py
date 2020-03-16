"""
Custom exceptions for the AIR SDK
"""
class AirError(Exception):
    """
    Base exception class. All custom exceptions should inherit from this class.
    """

class AirAuthorizationError(AirError):
    """ Raised when authorization with the API fails. """
    def __init__(self, message='An error occurred when authorizing the Cumulus AIR API'):
        self.message = message
        super().__init__(self.message)
