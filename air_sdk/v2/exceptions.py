# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
SDK-specific exceptions
"""

from typing import Optional


class AirError(Exception):
    def __init__(
        self,
        message: str = 'An error occurred within the air_sdk.v2.AirApi',
        status_code: Optional[int] = None,
    ):
        self.status_code = status_code
        super().__init__(message)


class AirModelAttributeError(AirError):
    def __init__(
        self,
        message: str = 'An error occurred while accessing an AirModel attribute.',
        status_code: Optional[int] = None,
    ):
        self.message = message
        super().__init__(message=self.message, status_code=status_code)
