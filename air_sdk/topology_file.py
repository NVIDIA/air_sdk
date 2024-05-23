# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Topologyfile module
"""

from . import util
from .air_model import AirModel


class TopologyFile(AirModel):
    """A text file that describes a network topology."""

    _deletable = False
    _updatable = False

    def __repr__(self):
        return f'<TopologyFile {self.id}>'


class TopologyFileApi:
    """High-level interface for the TopologyFile API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url.replace('v1', 'v2') + '/topology-file/'

    def get(self, file_id: str, **kwargs) -> TopologyFile:
        """
        Get an existing topology file

        Arguments:
            file_id (str): TopologyFile ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        TopologyFile

        Raises:
        AirUnexpectedResponse - API did not return a 200 OK or valid response JSON

        Example:
        ```
        >>> air.topology_files.get('5cec8f3b-f449-47a3-a6ee-c5b81bf92ccf')
        <TopologyFile 5cec8f3b-f449-47a3-a6ee-c5b81bf92ccf>
        ```
        """
        url = f'{self.url}{file_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return TopologyFile(self, **res.json())

    # TODO: v2 list APIs require pagination handling
    # def list(self, **kwargs) -> 'list[TopologyFile]':
    #     """
    #     List existing TopologyFiles

    #     Arguments:
    #         kwargs (dict, optional): All other optional keyword arguments are applied as query
    #             parameters/filters

    #     Returns:
    #     list[TopologyFile]

    #     Raises:
    #     AirUnexpectedResponse - API did not return a 200 OK or valid response JSON

    #     Example:
    #     ```
    #     >>> air.topology_files.list()
    #     [<TopologyFile 5cec8f3b-f449-47a3-a6ee-c5b81bf92ccf>, <TopologyFile 811490b5-d2ef-4775-948a-2c1fbe0ce939>]
    #     ```
    #     """
