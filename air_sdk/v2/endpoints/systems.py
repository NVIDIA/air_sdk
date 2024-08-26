# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from typing import Any

from air_sdk.v2.air_model import AirModel, BaseEndpointApi, PrimaryKey, ApiNotImplementedMixin


@dataclass(eq=False)
class System(ApiNotImplementedMixin, AirModel):
    id: str

    @classmethod
    def get_model_api(cls):
        return SystemEndpointApi


class SystemEndpointApi(BaseEndpointApi[System]):
    API_PATH = 'systems'  # A placeholder
    model = System

    def get(self, pk: PrimaryKey, **params: Any) -> System:
        return self.load_model({'id': str(pk)})
