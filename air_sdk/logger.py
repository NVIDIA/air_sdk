# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Logger module
"""
import logging
import re


def _redact(record):
    """Redact any strings in the log message that match a sensitive pattern"""
    sensitive_patterns = [r'(password[\'\"]:\s?[\'\"]).*([\'\"])']
    for pattern in sensitive_patterns:
        record.msg = re.sub(pattern, r'\g<1>***\g<2>', record.msg)
    return record


air_sdk_logger = logging.getLogger('air_sdk')  # pylint: disable=invalid-name
air_sdk_logger.addHandler(logging.NullHandler())
air_sdk_logger.addFilter(_redact)
