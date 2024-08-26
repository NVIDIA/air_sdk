# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from http import HTTPStatus

import pytest
import faker

from air_sdk.v2 import AirModelAttributeError
from air_sdk.v2.utils import join_urls

faker.Faker.seed(0)
fake = faker.Faker()


class TestWorkerEndpointApi:
    def test_list(self, api, run_list_test, worker_factory):
        run_list_test(api.workers, worker_factory)

    @pytest.mark.parametrize(
        'contact,is_valid',
        (
            (fake.email(), True),
            (fake.pylist(value_types=(str,)), True),
            (fake.pydict(value_types=(str,)), True),
            (None, False),
            (fake.pyint(), False),
        ),
    )
    def test_contact_field_response(self, api, worker_factory, contact, is_valid):
        if is_valid:
            worker = worker_factory(api, contact=contact)
            assert worker.contact == contact
        else:
            with pytest.raises(AirModelAttributeError):
                worker_factory(api, contact=contact)

    def test_refresh(self, api, run_refresh_test, worker_factory):
        run_refresh_test(api.workers, worker_factory)

    def test_heartbeat(self, api, setup_mock_responses, worker_factory):
        worker = worker_factory(api)
        setup_mock_responses(
            {('GET', join_urls(api.workers.url, 'heartbeat')): {'status_code': HTTPStatus.OK}}
        )
        worker.heartbeat()

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({}, True),
            ({'invalid_key': fake.slug()}, False),
            ({'airstrike_version': fake.slug()}, True),
            ({'architecture': fake.slug()}, True),
            ({'docker': fake.slug()}, True),
            ({'kernel': fake.slug()}, True),
            ({'libvirt': fake.slug()}, True),
            ({'operating_system': fake.slug()}, True),
            ({'proxy_image': fake.slug()}, True),
            ({'worker_version': fake.slug()}, True),
            (
                {
                    'airstrike_version': fake.slug(),
                    'architecture': fake.slug(),
                    'docker': fake.slug(),
                    'kernel': fake.slug(),
                    'libvirt': fake.slug(),
                    'operating_system': fake.slug(),
                    'proxy_image': fake.slug(),
                    'worker_version': fake.slug(),
                },
                True,
            ),
        ),
    )
    def test_update_inventory(self, api, setup_mock_responses, worker_factory, payload, is_valid):
        worker = worker_factory(api)
        setup_mock_responses(
            {('PUT', join_urls(api.workers.url, 'inventory')): {'status_code': HTTPStatus.OK}}
        )
        if is_valid:
            worker.update_inventory(**payload)
        else:
            with pytest.raises(Exception) as err:
                worker.update_inventory(**payload)
            assert err.type in (TypeError, ValueError)
