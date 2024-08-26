# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

# ruff:noqa: F401

__all__ = [
    'AccountEndpointApi',
    'Account',
    'AnnouncementEndpointApi',
    'Announcement',
    'ApiTokenEndpointApi',
    'ApiToken',
    'CloudInitEndpointApi',
    'CloudInit',
    'ImageEndpointApi',
    'Image',
    'InterfaceEndpointApi',
    'Interface',
    'JobEndpointApi',
    'Job',
    'Link',
    'LinkEndpointApi',
    'MarketplaceDemoEndpointApi',
    'MarketplaceDemo',
    'MarketplaceDemoTagsEndpointApi',
    'MarketplaceDemoTag',
    'NodeEndpointApi',
    'Node',
    'OrganizationEndpointApi',
    'Organization',
    'ResourceBudgetEndpointApi',
    'ResourceBudget',
    'ServiceEndpointApi',
    'Service',
    'SimulationEndpointApi',
    'Simulation',
    'SystemEndpointApi',
    'System',
    'UserConfigEndpointApi',
    'UserConfig',
    'WorkerEndpointApi',
    'Worker',
    'mixins',
]

from air_sdk.v2.endpoints.accounts import Account, AccountEndpointApi
from air_sdk.v2.endpoints.announcements import Announcement, AnnouncementEndpointApi
from air_sdk.v2.endpoints.api_tokens import ApiToken, ApiTokenEndpointApi
from air_sdk.v2.endpoints.images import Image, ImageEndpointApi
from air_sdk.v2.endpoints.interfaces import Interface, InterfaceEndpointApi, Link, LinkEndpointApi
from air_sdk.v2.endpoints.jobs import Job, JobEndpointApi
from air_sdk.v2.endpoints.marketplace_demo_tags import MarketplaceDemoTag, MarketplaceDemoTagsEndpointApi
from air_sdk.v2.endpoints.marketplace_demos import MarketplaceDemo, MarketplaceDemoEndpointApi
from air_sdk.v2.endpoints.nodes import Node, NodeEndpointApi
from air_sdk.v2.endpoints.cloud_inits import CloudInit, CloudInitEndpointApi
from air_sdk.v2.endpoints.organizations import Organization, OrganizationEndpointApi
from air_sdk.v2.endpoints.resource_budgets import ResourceBudget, ResourceBudgetEndpointApi
from air_sdk.v2.endpoints.services import Service, ServiceEndpointApi
from air_sdk.v2.endpoints.simulations import Simulation, SimulationEndpointApi
from air_sdk.v2.endpoints.systems import System, SystemEndpointApi
from air_sdk.v2.endpoints.user_configs import UserConfig, UserConfigEndpointApi
from air_sdk.v2.endpoints.workers import Worker, WorkerEndpointApi
from air_sdk.v2.endpoints import mixins
