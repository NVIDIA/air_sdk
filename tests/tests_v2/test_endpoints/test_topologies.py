# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from http import HTTPStatus

import faker
import pytest

from air_sdk.v2.utils import join_urls
from air_sdk.v2.endpoints.topologies import TopologyEndpointApi
from air_sdk.exceptions import AirUnexpectedResponse

faker.Faker.seed(0)
fake = faker.Faker()


@pytest.mark.parametrize(
    'payload, is_valid',
    [
        (  # Valid case
            {
                'source_format': 'DOT',
                'destination_format': 'JSON',
                'topology_data': 'graph "Valid Topology" {\r\n "node-1" [ os="generic/ubuntu2204" cpu=1 ]}',
            },
            True,
        ),
        (  # Valid case: Multiple nodes with connections
            {
                'source_format': 'DOT',
                'destination_format': 'JSON',
                'topology_data': """
                    graph "Multi Node Topology" {
                        "node-1" [ os="generic/ubuntu2204" cpu=2 ];
                        "node-2" [ os="generic/ubuntu2204" cpu=1 ];
                        "node-1" -- "node-2" [ bandwidth="1" ];
                    }
                """,
            },
            True,
        ),
        (  # Valid case: Complex topology with multiple connections
            {
                'source_format': 'DOT',
                'destination_format': 'JSON',
                'topology_data': """
                    graph "Complex Topology" {
                        "server-1" [ os="generic/ubuntu2204" cpu=4 memory="2048" ];
                        "server-2" [ os="generic/ubuntu2204" cpu=2 memory="2048" ];
                        "switch-1" [ type="switch" ];
                        "server-1" -- "switch-1" [ bandwidth="10Gbps" ];
                        "server-2" -- "switch-1" [ bandwidth="10Gbps" ];
                    }
                """,
            },
            True,
        ),
        (  # Invalid case: Missing required field
            {
                'source_format': 'DOT',
                'destination_format': 'JSON',
            },
            False,
        ),
        (  # Invalid case: Malformed DOT syntax
            {
                'source_format': 'DOT',
                'destination_format': 'JSON',
                'topology_data': 'graph "Invalid Topology" { invalid syntax here }',
            },
            False,
        ),
        (  # Invalid case: Empty topology
            {
                'source_format': 'DOT',
                'destination_format': 'JSON',
                'topology_data': '',
            },
            False,
        ),
        (  # Invalid case: Wrong source format
            {
                'source_format': 'INVALID',
                'destination_format': 'JSON',
                'topology_data': 'graph "Valid Topology" { "node-1" }',
            },
            False,
        ),
    ],
)
def test_parse_conversion(setup_mock_responses, api, payload, is_valid):
    endpoint_api = api.topologies
    parse_url = join_urls(api.topologies.url_v1, TopologyEndpointApi.PARSE_PATH)

    if is_valid:
        expected_response = {
            'source_format': payload['source_format'],
            'destination_format': payload['destination_format'],
            'topology_data': payload['topology_data'],
        }

        setup_mock_responses(
            {
                ('POST', parse_url): {
                    'json': expected_response,
                    'status_code': HTTPStatus.OK,
                }
            }
        )

        response = endpoint_api.parse(**payload)

        assert response['source_format'] == payload['source_format']
        assert response['destination_format'] == payload['destination_format']
        assert response['topology_data'] == payload['topology_data']

    else:
        setup_mock_responses(
            {
                ('POST', parse_url): {
                    'json': {'error': 'Invalid request'},
                    'status_code': HTTPStatus.BAD_REQUEST,
                }
            }
        )
        with pytest.raises(Exception) as err:
            endpoint_api.parse(**payload)

        assert err.type in (AirUnexpectedResponse, TypeError, ValueError)
