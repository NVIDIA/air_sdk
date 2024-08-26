# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT


import faker

from air_sdk import v2

faker.Faker.seed(0)
fake = faker.Faker()


class TestMarketplaceDemoTagsEndpointApi:
    def setup_method(self):
        self.AirApi = v2.AirApi
        self.api_url = 'https://air-fake-test.nvidia.com/api/'
        self.api = self.AirApi(api_url=self.api_url, authenticate=False)
        self.endpoint_url = v2.utils.join_urls(self.api_url, 'v2', self.api.marketplace_demo_tags.API_PATH)

    def test_list_single_inst(self, api, setup_mock_responses, marketplace_demo_tag_factory):
        """Ensure list requests work when there is only one page in the paginated response."""
        # Set up mock client
        results = [marketplace_demo_tag_factory(api).dict()]
        expected_responses = {
            ('GET', self.endpoint_url): {
                'json': {'previous': None, 'next': None, 'count': len(results), 'results': results},
                'status_code': 200,
            }
        }
        setup_mock_responses(expected_responses)
        # Test SDK

        tags = list(self.api.marketplace_demo_tags.list(limit=len(results)))
        assert len(tags) == 1
        assert isinstance(tags[0], self.api.marketplace_demo_tags.model)

    def test_pagination(self, api, setup_mock_responses, marketplace_demo_tag_factory):
        """Ensure multiple calls are made to collect paginated responses."""
        first_tag = marketplace_demo_tag_factory(api)
        second_tag = marketplace_demo_tag_factory(api)
        page_size = 1
        first_url = self.endpoint_url + f'?limit={page_size}'
        second_url = first_url + '&offset=1'
        expected_responses = {
            ('GET', first_url): {
                'json': {
                    'previous': None,
                    'next': second_url,
                    'count': page_size,
                    'results': [first_tag.dict()],
                },
                'status_code': 200,
            },
            ('GET', second_url): {
                'json': {
                    'previous': first_url,
                    'next': None,
                    'count': page_size,
                    'results': [second_tag.dict()],
                },
                'status_code': 200,
            },
        }
        setup_mock_responses(expected_responses)
        # Test SDK
        tags = list(self.api.marketplace_demo_tags.list(limit=page_size))
        assert len(tags) == 2
        assert tags[0] == first_tag
        assert tags[1] == second_tag
