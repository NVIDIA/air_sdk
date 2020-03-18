"""
Tests for util.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,no-self-use

from unittest import TestCase
import pytest
from requests import get
import requests_mock
import cumulus_air_sdk.air_sdk as sdk

class TestUtil(TestCase):
    @requests_mock.Mocker()
    def test_raise_if_invalid_response(self, mock_requests):
        mock_requests.get('http://test/api/v1/', status_code=201, json={})
        res = get('http://test/api/v1/')
        sdk.util.raise_if_invalid_response(res, 201)

    @requests_mock.Mocker()
    def test_raise_if_invalid_response_bad_code(self, mock_requests):
        mock_requests.get('http://test/api/v1/', status_code=200, json={})
        res = get('http://test/api/v1/')
        with pytest.raises(sdk.exceptions.AirUnexpectedResponse) as err:
            sdk.util.raise_if_invalid_response(res, 201)
            self.assertEqual(err.value, 200)

    @requests_mock.Mocker()
    def test_raise_if_invalid_response_bad_json(self, mock_requests):
        mock_requests.get('http://test/api/v1/', status_code=200, text='foo')
        res = get('http://test/api/v1/')
        with pytest.raises(sdk.exceptions.AirUnexpectedResponse) as err:
            sdk.util.raise_if_invalid_response(res)
            self.assertEqual(err.value, 'foo')
