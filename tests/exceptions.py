# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for exceptions.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring

from unittest import TestCase

from ..air_sdk import exceptions

class TestAirError(TestCase):
    def test_init(self):
        err = exceptions.AirError('test', 200)
        self.assertEqual(str(err), 'test')
        self.assertEqual(err.status_code, 200)

class TestAirAuthorizationError(TestCase):
    def test_init(self):
        err = exceptions.AirAuthorizationError('test', 200)
        self.assertEqual(err.message, 'test')
        self.assertEqual(err.status_code, 200)
        self.assertIsInstance(err, exceptions.AirError)

    def test_init_default(self):
        err = exceptions.AirAuthorizationError(status_code=200)
        self.assertEqual(err.message, 'An error occurred when authorizing the Air API')
        self.assertEqual(err.status_code, 200)

class TestAirUnexpectedResponse(TestCase):
    def test_init(self):
        err = exceptions.AirUnexpectedResponse('test')
        self.assertEqual(err.message,
                         'Received an unexpected response from the Air API: test')
        self.assertIsNone(err.status_code)
        self.assertIsInstance(err, exceptions.AirError)

    def test_init_status_code(self):
        err = exceptions.AirUnexpectedResponse('test', status_code=200)
        self.assertEqual(err.message,
                         'Received an unexpected response from the Air API (200): test')
        self.assertEqual(err.status_code, 200)

class TestAirForbiddenError(TestCase):
    def test_init(self):
        err = exceptions.AirForbiddenError('test')
        self.assertEqual(err.message, 'test')
        self.assertEqual(err.status_code, 403)
        self.assertIsInstance(err, exceptions.AirError)

    def test_init_default(self):
        err = exceptions.AirForbiddenError()
        self.assertEqual(err.message, 'Received 403 Forbidden. Please call AirApi.authorize().')
        self.assertEqual(err.status_code, 403)

class TestAirObjectDeleted(TestCase):
    def test_init(self):
        err = exceptions.AirObjectDeleted('foo', 'test')
        self.assertEqual(err.message, 'test')
        self.assertIsInstance(err, exceptions.AirError)

    def test_init_default(self):
        err = exceptions.AirObjectDeleted('foo')
        self.assertEqual(err.message,
                         'foo object has been deleted and should no longer be referenced')
