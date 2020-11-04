"""
Tests for exceptions.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring

from unittest import TestCase

from cumulus_air_sdk.air_sdk import exceptions

class TestAirForbiddenError(TestCase):
    def setUp(self):
        self.err = exceptions.AirForbiddenError()

    def test_init(self):
        self.assertIsInstance(self.err, exceptions.AirError)
        self.assertEqual(self.err.message,
                         'Received 403 Forbidden. Please call AirApi.authorize().')
        self.err.status_code = 403

    def test_init_message(self):
        err = exceptions.AirForbiddenError('test')
        self.assertEqual(err.message, 'test')
