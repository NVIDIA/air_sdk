# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from typing import List, Optional, Union

from air_sdk.v2.air_model import AirModel, BaseEndpointApi, DataDict, PrimaryKey
from air_sdk.v2.endpoints import mixins
from air_sdk.v2.endpoints.accounts import Account
from air_sdk.v2.endpoints.images import Image
from air_sdk.v2.endpoints.organizations import Organization


@dataclass(eq=False)
class Manifest(AirModel):
    id: str = field(repr=False)
    artifacts_directory: str = field(repr=False)
    artifacts_directory_max_size_gb: int = field(repr=False)
    boot_group: int = field(repr=False)
    configure_node_properties: DataDict = field(repr=False)
    configure_simulator: DataDict = field(repr=False)
    docker_run_parameters: DataDict = field(repr=False)
    emulation_type: str
    organization: Optional[Organization] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    owner: Optional[Account] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    platform_information: DataDict = field(repr=False)
    simulation_engine_versions: List[str] = field(repr=False)
    simulator_image: Image = field(metadata=AirModel.FIELD_FOREIGN_KEY)
    simulator_resources: DataDict = field(repr=False)
    emulation_params: DataDict = field(repr=False)

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return ManifestEndpointApi


class ManifestEndpointApi(
    mixins.ListApiMixin[Manifest],
    mixins.CreateApiMixin[Manifest],
    mixins.GetApiMixin[Manifest],
    mixins.PatchApiMixin[Manifest],
    mixins.PutApiMixin[Manifest],
    mixins.DeleteApiMixin,
    BaseEndpointApi[Manifest],
):
    API_PATH = 'manifests'
    model = Manifest

    def create(
        self,
        artifacts_directory: str,
        configure_node_properties: DataDict,
        configure_simulator: DataDict,
        docker_run_parameters: DataDict,
        emulation_type: str,
        organization: Union[Organization, PrimaryKey],
        simulator_image: Union[Image, PrimaryKey],
        simulator_resources: DataDict,
        artifacts_directory_max_size_gb: Optional[int] = None,
        boot_group: Optional[int] = None,
        platform_information: Optional[DataDict] = None,
        simulation_engine_versions: Optional[List[str]] = None,
        emulation_params: Optional[DataDict] = None,
    ) -> Manifest:
        payload: DataDict = {
            'artifacts_directory': artifacts_directory,
            'configure_node_properties': configure_node_properties,
            'configure_simulator': configure_simulator,
            'docker_run_parameters': docker_run_parameters,
            'emulation_type': emulation_type,
            'organization': organization,
            'simulator_image': simulator_image,
            'simulator_resources': simulator_resources,
        }
        for key, value in (
            ('artifacts_directory_max_size_gb', artifacts_directory_max_size_gb),
            ('boot_group', boot_group),
            ('platform_information', platform_information),
            ('simulation_engine_versions', simulation_engine_versions),
            ('emulation_params', emulation_params),
        ):
            if value is not None:  # Don't include optional None fields in payload.
                payload[key] = value
        return super().create(**payload)
