# SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT


from dataclasses import dataclass
from typing import Any, TypedDict, cast

from air_sdk.v2.endpoints.mixins import serialize_payload
from air_sdk.v2.air_model import AirModel, BaseEndpointApi, DataDict
from air_sdk.util import raise_if_invalid_response
from air_sdk.v2.utils import join_urls


class TopologyParseResponse(TypedDict):
    source_format: str
    destination_format: str
    topology_data: str


@dataclass(eq=False)
class Topology(AirModel):
    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return TopologyEndpointApi


class TopologyEndpointApi(BaseEndpointApi[Topology]):
    API_PATH = 'topology'
    PARSE_PATH = 'parse'
    model = Topology

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.url_v1 = join_urls(self.__api__.client.base_url.replace('/api/v2/', '/api/v1/'), self.API_PATH)

    def parse(self, source_format: str, destination_format: str, topology_data: str) -> TopologyParseResponse:
        """
        Parse topology data from one format to another.

        Args:
            source_format (str): The format of the input topology data
            destination_format (str): The desired output format
            topology_data (str): The topology data to parse

        Returns:
            TopologyParseResponse: The parsed topology data containing source_format, destination_format,
                                 topology_data
        """
        payload: DataDict = {
            'source_format': source_format,
            'destination_format': destination_format,
            'topology_data': topology_data,
        }
        parse_detail_url = join_urls(self.__api__.topologies.url_v1, self.PARSE_PATH)
        response = self.__api__.client.post(parse_detail_url, data=serialize_payload(payload))
        raise_if_invalid_response(response)
        return cast(TopologyParseResponse, response.json())
