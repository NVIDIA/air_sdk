# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for logger.py
"""
# pylint: disable=missing-function-docstring,missing-class-docstring,no-self-use,unused-argument

import logging
from unittest import TestCase
from unittest.mock import MagicMock

from air_sdk.logger import air_sdk_logger, _redact


class TestLogger(TestCase):
    def test_logger(self):
        self.assertEqual(air_sdk_logger.name, 'air_sdk')
        self.assertEqual(len(air_sdk_logger.handlers), 1)
        self.assertIsInstance(air_sdk_logger.handlers[0], logging.NullHandler)
        self.assertEqual(len(air_sdk_logger.filters), 1)
        self.assertEqual(air_sdk_logger.filters[0], _redact)

    def test_redact(self):
        record = MagicMock()
        record.msg = '{"password": "abc123"}'

        self.assertEqual(_redact(record).msg, '{"password": "***"}')

    def test_redact_no_op(self):
        msg = 'foo'
        record = MagicMock()
        record.msg = msg

        self.assertEqual(_redact(record).msg, msg)
