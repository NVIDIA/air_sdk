# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Tests for user_preference.py
"""
#pylint: disable=missing-function-docstring,missing-class-docstring,protected-access,unused-argument
import json
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..air_sdk import simulation, user_preference

class TestUserPreference(TestCase):
    def setUp(self):
        self.account_api = MagicMock()
        self.account_api.url = 'http://testserver/v1/account/'
        self.account_prefs = user_preference.UserPreference(self.account_api, preferences={'foo': 'bar'})
        self.sim_api = MagicMock()
        self.sim_api.url = 'http://testserver/v1/simulation/'
        self.sim = simulation.Simulation(self.sim_api)
        self.sim.id = 'abc123'
        self.sim_prefs = user_preference.UserPreference(self.sim_api, _model=self.sim,
                                                        preferences={'foo': 'bar'})

    def test_init(self):
        self.assertFalse(self.account_prefs._deletable)
        self.assertTrue(self.account_prefs._updatable)

    def test_repr(self):
        self.assertEqual(repr(self.account_prefs), json.dumps(self.account_prefs.preferences))

    @patch('air_sdk.air_sdk.user_preference.util.raise_if_invalid_response')
    def test_setattr(self, mock_raise):
        self.account_prefs.test = True
        self.account_api.client.patch.assert_called_once_with(self.account_prefs._url, json={'test': True})
        mock_raise.assert_called_once_with(self.account_api.client.patch.return_value)
        self.assertTrue(self.account_prefs.preferences['test'])

    @patch('air_sdk.air_sdk.user_preference.util.raise_if_invalid_response')
    @patch('air_sdk.air_sdk.user_preference.UserPreference._build_url', return_value=None)
    def test_setattr_super(self, *args):
        self.account_prefs._url = None
        pref = user_preference.UserPreference(self.sim_api, preferences={})

        pref.test = True
        self.sim_api.client.patch.assert_not_called()

    def test_build_url(self):
        self.assertEqual(self.account_prefs._build_url(), f'{self.account_api.url}preferences/')

    def test_build_url_model(self):
        self.assertEqual(self.sim_prefs._build_url(), f'{self.sim_api.url}{self.sim.id}/preferences/')

    def test_build_url_version_override(self):
        pref = user_preference.UserPreference(self.sim_api, _model=self.sim, _version_override='2')

        self.assertEqual(pref._build_url(),
                         f'{self.sim_api.url.replace("v1", "v2")}{self.sim.id}/preferences/')

    @patch('air_sdk.air_sdk.user_preference.UserPreference._load')
    def test_refresh(self, mock_load):
        self.account_prefs.refresh()
        mock_load.assert_called_once_with(**self.account_api.preferences().__dict__)

    @patch('air_sdk.air_sdk.simulation.Simulation.preferences')
    @patch('air_sdk.air_sdk.user_preference.UserPreference._load')
    def test_refresh_model(self, mock_load, *args):
        self.sim_prefs.refresh()
        mock_load.assert_called_once_with(**self.sim.preferences().__dict__)

    @patch('air_sdk.air_sdk.user_preference.util.raise_if_invalid_response')
    @patch('air_sdk.air_sdk.user_preference.UserPreference.refresh')
    def test_update(self, mock_refresh, mock_raise):
        self.account_prefs.update(test=True)
        mock_refresh.assert_called_once()
        self.assertTrue(self.account_prefs.preferences['test'])
        self.account_api.client.put.assert_called_once_with(self.account_prefs._url,
                                                            json=self.account_prefs.__dict__)
        mock_raise.assert_called_once_with(self.account_api.client.put.return_value)
