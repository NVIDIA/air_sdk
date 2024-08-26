# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
import logging
import uuid
from datetime import timedelta
from unittest.mock import patch

import faker
import pytest

from air_sdk import v2, const

faker.Faker.seed(0)
fake = faker.Faker()


class TestAirApi:
    def setup_method(self):
        self.AirApi = v2.AirApi
        self.username = str(uuid.uuid4())
        self.password = str(uuid.uuid4())
        self.api_url = f'https://air-{fake.slug()}.nvidia.com'
        self.v2_api_url = v2.utils.join_urls(self.api_url, 'api', 'v2')

    def test_client_setup_username_and_password(self):
        """Ensure the client's url and authentication were correctly set."""
        fake_jwt = str(uuid.uuid4())
        with patch('air_sdk.v2.client.Client.get_token') as mock_get_token:
            mock_get_token.return_value = fake_jwt
            api = self.AirApi(api_url=self.api_url, username=self.username, password=self.password)
            assert type(api.client) is v2.client.Client
            assert api.client.base_url == self.v2_api_url
            assert 'content-type' in api.client.headers.keys(), 'A default content-type should be set'
            # Ensure we have an authentication token
            mock_get_token.assert_called_once_with(self.username, self.password)
            assert (
                api.client.headers['Authorization'] == f'Bearer {fake_jwt}'
            ), 'Authorization token was not set'

    def test_client_setup_bearer_token(self):
        """Ensure we use the bearer_token provided."""
        bearer_token = str(uuid.uuid4())
        with patch('air_sdk.v2.client.Client.get_token') as mock_get_token:
            api = self.AirApi(api_url=self.api_url, bearer_token=bearer_token)
            mock_get_token.assert_not_called()
            assert type(api.client) is v2.client.Client
            assert api.client.base_url == self.v2_api_url
            assert 'content-type' in api.client.headers.keys(), 'A default content-type should be set'
            # Ensure we have an authentication token
            assert (
                api.client.headers['Authorization'] == f'Bearer {bearer_token}'
            ), 'Authorization token was not set'

    @pytest.mark.parametrize(
        'extra_kwargs', [{}, {'username': str(uuid.uuid4())}, {'password': str(uuid.uuid4())}]
    )
    def test_client_no_auth_credentials_provided(self, extra_kwargs):
        with pytest.raises(ValueError):
            self.AirApi(api_url=self.api_url, **extra_kwargs)

    def test_client_can_skip_authentication(self):
        api = self.AirApi(api_url=self.api_url, authenticate=False)
        assert type(api.client) is v2.client.Client
        assert api.client.headers['Authorization'] is None, 'A blank Authorization should be set.'

    def test_default_timeouts(self, mock_client, setup_mock_responses, paginated_response):
        """Ensure we set a default timeout for all requests."""
        api = self.AirApi(api_url=self.api_url, authenticate=False)
        endpoint = api.marketplace_demo_tags
        setup_mock_responses({('GET', endpoint.url): paginated_response})
        list(endpoint.list())
        assert mock_client.call_count == 1
        assert mock_client.request_history[0]._timeout == (
            const.DEFAULT_CONNECT_TIMEOUT,
            const.DEFAULT_READ_TIMEOUT,
        )

    def test_custom_timeouts(self, mock_client, setup_mock_responses, paginated_response):
        """Ensure clients can set a custom timeouts for read/connect if they desire."""
        api = self.AirApi(api_url=self.api_url, authenticate=False)
        custom_connect_timeout = fake.pyint()
        custom_read_timeout = fake.pyint()
        api.set_connect_timeout(timedelta(seconds=custom_connect_timeout))
        api.set_read_timeout(timedelta(seconds=custom_read_timeout))
        endpoint = api.marketplace_demo_tags
        setup_mock_responses({('GET', endpoint.url): paginated_response})
        list(endpoint.list())
        assert mock_client.call_count == 1
        assert mock_client.request_history[0]._timeout == (custom_connect_timeout, custom_read_timeout)

    def test_each_request_is_logged(self, caplog, mock_client, setup_mock_responses, paginated_response):
        api = self.AirApi(api_url=self.api_url, authenticate=False)
        endpoint = api.marketplace_demo_tags
        setup_mock_responses({('GET', endpoint.url): paginated_response})
        with caplog.at_level(logging.DEBUG):
            assert list(endpoint.list()) == []
        assert str(caplog.records[-1].message == f'GET: {endpoint.url}')
