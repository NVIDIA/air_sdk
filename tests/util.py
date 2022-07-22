# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for util.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,no-self-use,unused-argument

import datetime

from json import JSONDecodeError
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import exceptions, util

class TestUtil(TestCase):
    def test_raise_if_invalid_response(self):
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.json.return_value = {'id': 'abc123'}
        util.raise_if_invalid_response(mock_res)

    def test_raise_if_invalid_response_status(self):
        mock_res = MagicMock()
        mock_res.status_code = 400
        with self.assertRaises(exceptions.AirUnexpectedResponse) as err:
            util.raise_if_invalid_response(mock_res)
        self.assertEqual(err.exception.message,
                         'Received an unexpected response from the Air API (400): ' +
                         str(mock_res.text))
        self.assertEqual(err.exception.status_code, 400)

    def test_raise_if_invalid_response_no_data(self):
        mock_res = MagicMock()
        mock_res.status_code = 200
        util.raise_if_invalid_response(mock_res, data_type=None)

    def test_raise_if_invalid_bad_json(self):
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.json.side_effect = JSONDecodeError('test', 'foo', 0)
        with self.assertRaises(exceptions.AirUnexpectedResponse) as err:
            util.raise_if_invalid_response(mock_res)
        self.assertEqual(err.exception.message,
                         'Received an unexpected response from the Air API (200): ' +
                         str(mock_res.text))
        self.assertEqual(err.exception.status_code, 200)

    def test_raise_if_invalid_bad_data_type(self):
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.json.return_value = {}
        with self.assertRaises(exceptions.AirUnexpectedResponse) as err:
            util.raise_if_invalid_response(mock_res, data_type=list)
        self.assertEqual(err.exception.message,
                         'Received an unexpected response from the Air API (200): ' + \
                         'Expected API response to be of type <class \'list\'>, ' + \
                         'got <class \'dict\'>')
        self.assertEqual(err.exception.status_code, 200)

    def test_required_kwargs(self):
        @util.required_kwargs(['foo', 'bar'])
        def decorated(**kwargs):
            pass
        with self.assertRaises(AttributeError) as err:
            decorated(foo='test')
        self.assertTrue('requires bar' in str(err.exception))

    def test_required_kwargs_str(self):
        @util.required_kwargs('foo')
        def decorated(**kwargs):
            pass
        with self.assertRaises(AttributeError) as err:
            decorated(f='test')
        self.assertTrue('requires foo' in str(err.exception))

    @patch('logging.warning')
    def test_deprecated(self, mock_log):
        @util.deprecated()
        def decorated():
            pass
        decorated()
        self.assertTrue('has been deprecated and will be removed in a future release.' \
                        in mock_log.call_args[0][0])

    @patch('logging.warning')
    def test_deprecated_new(self, mock_log):
        @util.deprecated('new_func')
        def decorated():
            pass
        decorated()
        self.assertTrue('has been deprecated and will be removed in a future release. ' + \
                        'Use new_func instead.' in mock_log.call_args[0][0])

    @patch('logging.warning')
    def test_validate_timestamps(self, mock_log):
        now = datetime.datetime.now()
        past = now - datetime.timedelta(hours=8)
        util.validate_timestamps('Simulation created', expires_at=None, sleep_at=past)
        log = mock_log.call_args[0][0]
        self.assertTrue(f'Simulation created with `sleep_at` in the past: {past}' in log)

    @patch('logging.warning')
    def test_validate_timestamps_future(self, mock_log):
        now = datetime.datetime.now()
        past = now - datetime.timedelta(hours=8)
        future = now + datetime.timedelta(hours=8)
        util.validate_timestamps('Simulation created', expires_at=past, sleep_at=future)
        log = mock_log.call_args[0][0]
        self.assertTrue(f'Simulation created with `expires_at` in the past: {past}' in log)
