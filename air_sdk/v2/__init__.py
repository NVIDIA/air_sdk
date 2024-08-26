# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from datetime import timedelta
from typing import Optional

from air_sdk import const
from air_sdk.v2 import utils
from air_sdk.v2.client import Client

__all__ = ['const', 'AirApi', 'Client', 'utils', 'AirModelAttributeError']

from air_sdk.v2.exceptions import AirError, AirModelAttributeError


class AirApi:
    def __init__(
        self,
        api_url: str = const.DEFAULT_API_URL,
        username: Optional[str] = None,
        password: Optional[str] = None,
        bearer_token: Optional[str] = None,
        authenticate: bool = True,
    ):
        # Setup client session
        self.client = Client(api_url=api_url)
        if authenticate:
            self.client.authenticate(
                username=username,
                password=password,
                bearer_token=bearer_token,
            )

    @property
    def accounts(self):
        from .endpoints import AccountEndpointApi

        return AccountEndpointApi(self)

    @property
    def announcements(self):
        from .endpoints import AnnouncementEndpointApi

        return AnnouncementEndpointApi(self)

    @property
    def api_tokens(self):
        from .endpoints import ApiTokenEndpointApi

        return ApiTokenEndpointApi(self)

    @property
    def cloud_inits(self):
        from air_sdk.v2.endpoints import CloudInitEndpointApi

        return CloudInitEndpointApi(self)

    @property
    def images(self):
        from .endpoints import ImageEndpointApi

        return ImageEndpointApi(self)

    @property
    def interfaces(self):
        from .endpoints import InterfaceEndpointApi

        return InterfaceEndpointApi(self)

    @property
    def jobs(self):
        from .endpoints import JobEndpointApi

        return JobEndpointApi(self)

    @property
    def links(self):
        from air_sdk.v2.endpoints import LinkEndpointApi

        return LinkEndpointApi(self)

    @property
    def marketplace_demos(self):
        from .endpoints import MarketplaceDemoEndpointApi

        return MarketplaceDemoEndpointApi(self)

    @property
    def marketplace_demo_tags(self):
        from .endpoints import MarketplaceDemoTagsEndpointApi

        return MarketplaceDemoTagsEndpointApi(self)

    @property
    def nodes(self):
        from .endpoints import NodeEndpointApi

        return NodeEndpointApi(self)

    @property
    def organizations(self):
        from .endpoints import OrganizationEndpointApi

        return OrganizationEndpointApi(self)

    @property
    def resource_budgets(self):
        from .endpoints import ResourceBudgetEndpointApi

        return ResourceBudgetEndpointApi(self)

    @property
    def services(self):
        from .endpoints import ServiceEndpointApi

        return ServiceEndpointApi(self)

    @property
    def simulations(self):
        from .endpoints import SimulationEndpointApi

        return SimulationEndpointApi(self)

    @property
    def systems(self):
        from .endpoints import SystemEndpointApi

        return SystemEndpointApi(self)

    @property
    def user_configs(self):
        from .endpoints import UserConfigEndpointApi

        return UserConfigEndpointApi(self)

    @property
    def workers(self):
        from .endpoints import WorkerEndpointApi

        return WorkerEndpointApi(self)

    def set_connect_timeout(self, t_delta: timedelta) -> None:
        self.client.connect_timeout = int(t_delta.total_seconds())

    def set_read_timeout(self, t_delta: timedelta) -> None:
        self.client.read_timeout = int(t_delta.total_seconds())

    def set_page_size(self, n: int) -> None:
        """Set the page size of paginated responses."""
        if isinstance(n, int) and n > 0:
            self.client.pagination_page_size = n
        else:
            raise AirError('Pagination page size must be a positive integer.')
