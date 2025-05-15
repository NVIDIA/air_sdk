# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Optional

from air_sdk import const
from air_sdk.v2 import utils
from air_sdk.v2.client import Client

__all__ = ['const', 'AirApi', 'Client', 'utils', 'AirModelAttributeError']


from air_sdk.v2.exceptions import AirError, AirModelAttributeError

if TYPE_CHECKING:
    from air_sdk.v2.endpoints import (
        AccountEndpointApi,
        AnnouncementEndpointApi,
        ApiTokenEndpointApi,
        BreakoutEndpointApi,
        CloudInitEndpointApi,
        FleetEndpointApi,
        ImageEndpointApi,
        InterfaceEndpointApi,
        JobEndpointApi,
        LinkEndpointApi,
        ManifestEndpointApi,
        MarketplaceDemoEndpointApi,
        MarketplaceDemoTagsEndpointApi,
        NodeEndpointApi,
        OrganizationEndpointApi,
        ResourceBudgetEndpointApi,
        ServiceEndpointApi,
        SimulationEndpointApi,
        SystemEndpointApi,
        TopologyEndpointApi,
        UserConfigEndpointApi,
        WorkerEndpointApi,
        NodeInstructionsEndpointApi,
    )


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
    def accounts(self) -> AccountEndpointApi:
        from .endpoints import AccountEndpointApi

        return AccountEndpointApi(self)

    @property
    def announcements(self) -> AnnouncementEndpointApi:
        from .endpoints import AnnouncementEndpointApi

        return AnnouncementEndpointApi(self)

    @property
    def api_tokens(self) -> ApiTokenEndpointApi:
        from .endpoints import ApiTokenEndpointApi

        return ApiTokenEndpointApi(self)

    @property
    def breakouts(self) -> BreakoutEndpointApi:
        from .endpoints import BreakoutEndpointApi

        return BreakoutEndpointApi(self)

    @property
    def cloud_inits(self) -> CloudInitEndpointApi:
        from air_sdk.v2.endpoints import CloudInitEndpointApi

        return CloudInitEndpointApi(self)

    @property
    def fleets(self) -> FleetEndpointApi:
        from .endpoints import FleetEndpointApi

        return FleetEndpointApi(self)

    @property
    def images(self) -> ImageEndpointApi:
        from .endpoints import ImageEndpointApi

        return ImageEndpointApi(self)

    @property
    def interfaces(self) -> InterfaceEndpointApi:
        from .endpoints import InterfaceEndpointApi

        return InterfaceEndpointApi(self)

    @property
    def jobs(self) -> JobEndpointApi:
        from .endpoints import JobEndpointApi

        return JobEndpointApi(self)

    @property
    def manifests(self) -> ManifestEndpointApi:
        from .endpoints import ManifestEndpointApi

        return ManifestEndpointApi(self)

    @property
    def links(self) -> LinkEndpointApi:
        from air_sdk.v2.endpoints import LinkEndpointApi

        return LinkEndpointApi(self)

    @property
    def marketplace_demos(self) -> MarketplaceDemoEndpointApi:
        from .endpoints import MarketplaceDemoEndpointApi

        return MarketplaceDemoEndpointApi(self)

    @property
    def marketplace_demo_tags(self) -> MarketplaceDemoTagsEndpointApi:
        from .endpoints import MarketplaceDemoTagsEndpointApi

        return MarketplaceDemoTagsEndpointApi(self)

    @property
    def nodes(self) -> NodeEndpointApi:
        from .endpoints import NodeEndpointApi

        return NodeEndpointApi(self)

    @property
    def organizations(self) -> OrganizationEndpointApi:
        from .endpoints import OrganizationEndpointApi

        return OrganizationEndpointApi(self)

    @property
    def resource_budgets(self) -> ResourceBudgetEndpointApi:
        from .endpoints import ResourceBudgetEndpointApi

        return ResourceBudgetEndpointApi(self)

    @property
    def services(self) -> ServiceEndpointApi:
        from .endpoints import ServiceEndpointApi

        return ServiceEndpointApi(self)

    @property
    def simulations(self) -> SimulationEndpointApi:
        from .endpoints import SimulationEndpointApi

        return SimulationEndpointApi(self)

    @property
    def systems(self) -> SystemEndpointApi:
        from .endpoints import SystemEndpointApi

        return SystemEndpointApi(self)

    @property
    def topologies(self) -> TopologyEndpointApi:
        from .endpoints import TopologyEndpointApi

        return TopologyEndpointApi(self)

    @property
    def user_configs(self) -> UserConfigEndpointApi:
        from .endpoints import UserConfigEndpointApi

        return UserConfigEndpointApi(self)

    @property
    def workers(self) -> WorkerEndpointApi:
        from .endpoints import WorkerEndpointApi

        return WorkerEndpointApi(self)

    @property
    def node_instructions(self) -> NodeInstructionsEndpointApi:
        from .endpoints import NodeInstructionsEndpointApi

        return NodeInstructionsEndpointApi(self)

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
