# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Constants shared throughout the SDK.
"""

ALLOWED_HOSTS = [
    'air.nvidia.com',
    'staging.air.nvidia.com',
    'air.cumulusnetworks.com',
    'staging.air.cumulusnetworks.com',
]

DEFAULT_API_URL = 'https://air.nvidia.com/api/'


DEFAULT_CONNECT_TIMEOUT = 16  # seconds
DEFAULT_READ_TIMEOUT = 61  # seconds
DEFAULT_PAGINATION_PAGE_SIZE = 200  # Objects per paginated response
