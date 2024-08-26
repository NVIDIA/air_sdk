# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from typing import Dict, Any, Optional
from json import JSONDecodeError
from urllib.parse import urlparse

import requests  # type: ignore[import-untyped]

from air_sdk.v2.utils import join_urls
from air_sdk import logger, const
from air_sdk.air_api import AirAuthorizationError, _normalize_api_url  # type: ignore[attr-defined]


class Client(requests.Session):  # type: ignore
    """A session client for managing the execution of API requests."""

    def __init__(self, api_url: str):
        super().__init__()
        self.headers.update({'content-type': 'application/json', 'Authorization': None})
        self.api_url = _normalize_api_url(api_url)
        self.base_url = join_urls(self.api_url, 'v2')
        self.connect_timeout = const.DEFAULT_CONNECT_TIMEOUT
        self.read_timeout = const.DEFAULT_READ_TIMEOUT
        self.pagination_page_size = const.DEFAULT_PAGINATION_PAGE_SIZE

    def rebuild_auth(self, prepared_request, response):
        """Allow credential sharing between nvidia.com and cumulusnetworks.com only"""
        if urlparse(prepared_request.url).hostname in const.ALLOWED_HOSTS:
            return
        super().rebuild_auth(prepared_request, response)

    def request(self, method: str, url: str, **kwargs: Dict[str, Any]) -> requests.Response:
        """Override request method to pass the timeout"""
        kwargs.setdefault('timeout', (self.connect_timeout, self.read_timeout))  # type: ignore[arg-type]
        return super().request(method, url, **kwargs)

    def authenticate(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        bearer_token: Optional[str] = None,
    ) -> None:
        if bearer_token is None and not (username and password):
            raise ValueError(
                'Unable to authenticate client. Please provide one of the following: '
                '(1) `username` and `password`; '
                '(2) `bearer_token`'
            )
        token = bearer_token or self.get_token(username, password)  # type: ignore[arg-type]
        self.headers.update({'authorization': f'Bearer {token}'})

    def get_token(self, username: str, password: str) -> str:
        login_url = join_urls(self.api_url, 'v1', 'login')
        response = self.post(login_url, json={'username': username, 'password': password})
        try:
            token = response.json().get('token', None)
            if isinstance(token, str):
                return token
            logger.debug('AirApi.get_token :: Response JSON')  # type: ignore
            logger.debug(response.json())  # type: ignore
            raise AirAuthorizationError('API did not provide a token for ' + username)
        except JSONDecodeError:
            raise AirAuthorizationError('API did not return a valid JSON response')
