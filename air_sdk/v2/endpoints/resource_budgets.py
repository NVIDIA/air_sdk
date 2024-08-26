# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from typing import Any, Optional

from air_sdk.v2.air_model import AirModel, BaseEndpointApi, PrimaryKey, ApiNotImplementedMixin


@dataclass(eq=False)
class ResourceBudget(ApiNotImplementedMixin, AirModel):
    id: str
    cpu: Optional[int] = field(repr=False)
    cpu_used: Optional[int] = field(repr=False)
    image_uploads: Optional[int] = field(repr=False)
    image_uploads_used: Optional[int] = field(repr=False)
    memory: Optional[int] = field(repr=False)
    memory_used: Optional[int] = field(repr=False)
    simulations: Optional[int] = field(repr=False)
    simulations_used: Optional[int] = field(repr=False)
    storage: Optional[int] = field(repr=False)
    storage_used: Optional[int] = field(repr=False)
    userconfigs: Optional[int] = field(repr=False)
    userconfigs_used: Optional[int] = field(repr=False)

    @classmethod
    def get_model_api(cls):
        return ResourceBudgetEndpointApi


class ResourceBudgetEndpointApi(BaseEndpointApi[ResourceBudget]):
    API_PATH = 'resource_budgets'  # A placeholder
    model = ResourceBudget

    def get(self, pk: PrimaryKey, **params: Any) -> ResourceBudget:
        return self.load_model({'id': str(pk)})
