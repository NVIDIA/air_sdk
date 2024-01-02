# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Custom exceptions for the AIR SDK
"""


class AirError(Exception):
    """
    Base exception class. All custom exceptions should inherit from this class.
    """

    def __init__(self, message='', status_code=None):
        self.status_code = status_code
        super().__init__(message)


class AirAuthorizationError(AirError):
    """Raised when authorization with the API fails."""

    def __init__(self, message='An error occurred when authorizing the Air API', status_code=None):
        self.message = message
        super().__init__(message=self.message, status_code=status_code)


class AirUnexpectedResponse(AirError):
    """Raised when the API returns an unexpected response."""

    def __init__(self, message='', status_code=None):
        self.message = 'Received an unexpected response from the Air API'
        if status_code:
            self.message += f' ({status_code})'
        self.message += f': {message}'
        super().__init__(message=self.message, status_code=status_code)


class AirForbiddenError(AirError):
    """Raised when an API call returns a 403 Forbidden error"""

    def __init__(self, message='Received 403 Forbidden. Please call AirApi.authorize().'):
        self.message = message
        super().__init__(message=self.message, status_code=403)


class AirObjectDeleted(AirError):
    """Raised when accessing a previously instantiated object that has since been deleted"""

    def __init__(self, cls, message=''):
        self.message = message
        if not self.message:
            self.message = f'{cls} object has been deleted and should no longer be referenced'
        super().__init__(message=self.message)
