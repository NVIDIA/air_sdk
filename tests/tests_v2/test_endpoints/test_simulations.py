# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

import itertools
import json
import tempfile
from datetime import timedelta, timezone
from http import HTTPStatus
from pathlib import Path
from typing import cast, get_args
from unittest.mock import MagicMock
from uuid import UUID

import faker
import pytest

import air_sdk.v2.endpoints.simulations
from air_sdk.exceptions import AirUnexpectedResponse
from air_sdk.v2.utils import join_urls

faker.Faker.seed(0)
fake = faker.Faker()


class TestSimulation:
    @pytest.mark.parametrize(
        'format',
        get_args(air_sdk.v2.endpoints.simulations.TopologyFormatType),
    )
    def test_export(self, api, simulation_factory, format):
        simulation = cast(air_sdk.v2.endpoints.simulations.Simulation, simulation_factory(api))
        simulation.__api__ = MagicMock(simulations=MagicMock(export=(mock_export := MagicMock())))
        return_value = simulation.export(
            format,
            (image_ids := MagicMock(spec=bool)),
        )

        mock_export.assert_called_with(simulation, format, image_ids)
        assert mock_export.return_value == return_value

    def test_load(self, api, simulation_factory, mock_client):
        simulation = cast(air_sdk.v2.endpoints.simulations.Simulation, simulation_factory(api))
        current_state = simulation.state
        desired_state = f'{simulation.state}_CHANGED'

        def _state_transition(*args, **kwargs):
            """Mimics state change on the backend"""
            nonlocal current_state
            current_state = desired_state
            return dict()

        def _state_refresh(*args, **kwargs):
            """Mimics state refresh at SDK level"""
            simulation.state = current_state
            return json.loads(simulation.json())

        mock_client.register_uri(
            'POST',
            join_urls(simulation.detail_url, 'load'),
            json=_state_transition,
            status_code=HTTPStatus.OK,
        )
        mock_client.register_uri(
            'GET',
            join_urls(simulation.detail_url),
            json=_state_refresh,
            status_code=HTTPStatus.OK,
        )
        simulation.load()
        assert simulation.state == desired_state

    def test_store(self, api, simulation_factory, mock_client):
        simulation = cast(air_sdk.v2.endpoints.simulations.Simulation, simulation_factory(api))
        current_state = simulation.state
        desired_state = f'{simulation.state}_CHANGED'

        def _state_transition(*args, **kwargs):
            """Mimics state change on the backend"""
            nonlocal current_state
            current_state = desired_state
            return dict()

        def _state_refresh(*args, **kwargs):
            """Mimics state refresh at SDK level"""
            simulation.state = current_state
            return json.loads(simulation.json())

        mock_client.register_uri(
            'POST',
            join_urls(simulation.detail_url, 'store'),
            json=_state_transition,
            status_code=HTTPStatus.OK,
        )
        mock_client.register_uri(
            'GET',
            simulation.detail_url,
            json=_state_refresh,
            status_code=HTTPStatus.OK,
        )
        simulation.store()
        assert simulation.state == desired_state

    def test_rebuild(self, api, simulation_factory, mock_client):
        simulation = cast(air_sdk.v2.endpoints.simulations.Simulation, simulation_factory(api))
        current_state = simulation.state
        desired_state = f'{simulation.state}_CHANGED'

        def _state_transition(*args, **kwargs):
            """Mimics state change on the backend"""
            nonlocal current_state
            current_state = desired_state
            return dict()

        def _state_refresh(*args, **kwargs):
            """Mimics state refresh at SDK level"""
            simulation.state = current_state
            return json.loads(simulation.json())

        mock_client.register_uri(
            'POST',
            join_urls(simulation.detail_url, 'rebuild'),
            json=_state_transition,
            status_code=HTTPStatus.OK,
        )
        mock_client.register_uri(
            'GET',
            simulation.detail_url,
            json=_state_refresh,
            status_code=HTTPStatus.OK,
        )
        simulation.rebuild()
        assert simulation.state == desired_state

    def test_extend(self, api, simulation_factory, mock_client):
        simulation = cast(air_sdk.v2.endpoints.simulations.Simulation, simulation_factory(api))
        current_sleep_at = simulation.sleep_at
        desired_sleep_at = simulation.sleep_at + timedelta(hours=12)

        def _extend_sleep(*args, **kwargs):
            """Mimics sleep time extension on the backend"""
            nonlocal current_sleep_at
            current_sleep_at = desired_sleep_at
            return dict()

        def _state_refresh(*args, **kwargs):
            """Mimics state refresh at SDK level"""
            simulation.sleep_at = current_sleep_at
            return json.loads(simulation.json())

        mock_client.register_uri(
            'POST',
            join_urls(simulation.detail_url, 'extend'),
            json=_extend_sleep,
            status_code=HTTPStatus.OK,
        )
        mock_client.register_uri(
            'GET',
            simulation.detail_url,
            json=_state_refresh,
            status_code=HTTPStatus.OK,
        )
        response = simulation.extend()
        assert response == desired_sleep_at

    def test_duplicate(self, api, simulation_factory, mock_client):
        simulation_original = cast(air_sdk.v2.endpoints.simulations.Simulation, simulation_factory(api))
        simulation_clone = cast(air_sdk.v2.endpoints.simulations.Simulation, simulation_factory(api))
        current_state = simulation_original.state
        desired_state = f'{simulation_original.state}_CHANGED'

        def _handle_duplication(*args, **kwargs):
            """Mimics simulation duplication on the backend"""
            nonlocal current_state
            current_state = desired_state
            return {'simulation': {'id': str(simulation_clone.__pk__)}}

        def _state_refresh(*args, **kwargs):
            """Mimics state refresh at SDK level"""
            simulation_original.state = current_state
            return json.loads(simulation_original.json())

        mock_client.register_uri(
            'POST',
            join_urls(simulation_original.detail_url, 'duplicate'),
            json=_handle_duplication,
            status_code=HTTPStatus.OK,
        )
        mock_client.register_uri(
            'GET',
            simulation_original.detail_url,
            json=_state_refresh,
            status_code=HTTPStatus.OK,
        )
        mock_client.register_uri(
            'GET',
            simulation_clone.detail_url,
            json=json.loads(simulation_clone.json()),
            status_code=HTTPStatus.OK,
        )
        response = simulation_original.duplicate()
        assert response == simulation_clone
        assert simulation_original.state == desired_state


class TestSimulationEndpointApi:
    def test_list(self, api, run_list_test, simulation_factory):
        run_list_test(api.simulations, simulation_factory)

    def test_refresh(self, api, run_refresh_test, simulation_factory):
        run_refresh_test(api.simulations, simulation_factory)

    def test_delete(self, api, run_delete_test, simulation_factory):
        run_delete_test(api.simulations, simulation_factory)

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({}, False),
            ({'title': None}, False),
            ({'title': fake.company()}, True),
            ({'title': fake.company(), 'random_field': fake.slug()}, False),
            (
                {
                    'title': fake.company(),
                    'documentation': fake.url(),
                    'expires': fake.pybool(),
                    'expires_at': fake.date_time(tzinfo=timezone.utc),
                    'organization': fake.uuid4(cast_to=str),
                    'metadata': json.dumps(fake.pydict(value_types=(str,))),
                    'owner': fake.email(),
                    'preferred_worker': fake.uuid4(cast_to=str),
                    'sleep': fake.pybool(),
                    'sleep_at': fake.date_time(tzinfo=timezone.utc),
                },
                True,
            ),
            ({'title': fake.company(), 'preferred_worker': fake.pyint()}, False),
            ({'title': fake.company(), 'organization': fake.pyint()}, False),
        ),
    )
    def test_create(self, api, simulation_factory, run_create_test_case, payload, is_valid):
        """This tests that the data provided is properly validated and used."""
        run_create_test_case(api.simulations, simulation_factory, payload, is_valid)

    def test_update(self, api, run_update_patch_test, simulation_factory, worker_factory):
        cases = (
            # Empty Case
            ({}, True),
            # None cases
            ({'documentation': None}, True),
            ({'expires': None}, True),
            ({'expires_at': None}, True),
            ({'metadata': None}, True),
            ({'preferred_worker': None}, True),
            ({'sleep': None}, True),
            ({'sleep_at': None}, True),
            ({'title': None}, True),
            # Valid data cases
            ({'documentation': fake.url()}, True),
            ({'documentation': fake.slug()}, True),
            ({'expires': fake.pybool()}, True),
            ({'expires_at': fake.date_time(tzinfo=timezone.utc)}, True),
            ({'metadata': json.dumps(fake.pydict(value_types=(str,)))}, True),
            ({'metadata': ''}, True),
            ({'preferred_worker': fake.uuid4(cast_to=str)}, True),
            ({'preferred_worker': fake.uuid4(cast_to=None)}, True),
            ({'preferred_worker': worker_factory(api)}, True),
            ({'sleep': fake.pybool()}, True),
            ({'sleep_at': fake.date_time(tzinfo=timezone.utc)}, True),
            ({'title': fake.company()}, True),
            ({'title': fake.uuid4(cast_to=str)}, True),
            # Invalid data cases
            ({'documentation': fake.pybool()}, False),
            ({'documentation': fake.pyint()}, False),
            ({'expires': fake.slug()}, False),
            ({'expires_at': fake.pybool()}, False),
            ({'metadata': fake.pydict(value_types=(str,))}, False),
            ({'metadata': fake.pybool()}, False),
            ({'preferred_worker': fake.pybool()}, False),
            ({'sleep': fake.slug()}, False),
            ({'sleep_at': fake.slug()}, False),
            ({'sleep_at': fake.pybool()}, False),
            ({'title': fake.pybool()}, False),
            ({'title': fake.pyint()}, False),
            ({'title': fake.uuid4(cast_to=None)}, False),
            # Unexpected field case
            ({fake.slug().replace('-', '_'): fake.slug()}, False),
        )
        for payload, is_valid in cases:
            run_update_patch_test(api.simulations, simulation_factory, payload, is_valid)

    def test_full_update(self, api, run_full_update_patch_test, simulation_factory, worker_factory):
        cases = (
            # Empty Case
            ({}, False),
            # Minimal data case
            (
                {
                    'documentation': None,
                    'expires': fake.pybool(),
                    'expires_at': fake.date_time(tzinfo=timezone.utc),
                    'metadata': None,
                    'preferred_worker': None,
                    'sleep': fake.pybool(),
                    'sleep_at': fake.date_time(tzinfo=timezone.utc),
                    'title': fake.company(),
                },
                True,
            ),
            # Full data cases
            (
                {
                    'documentation': fake.url(),
                    'expires': fake.pybool(),
                    'expires_at': fake.date_time(tzinfo=timezone.utc),
                    'metadata': json.dumps(fake.pydict(value_types=(str,))),
                    'preferred_worker': worker_factory(api),
                    'sleep': fake.pybool(),
                    'sleep_at': fake.date_time(tzinfo=timezone.utc),
                    'title': fake.company(),
                },
                True,
            ),
            (
                {
                    'documentation': fake.url(),
                    'expires': fake.pybool(),
                    'expires_at': fake.date_time(tzinfo=timezone.utc),
                    'metadata': json.dumps(fake.pydict(value_types=(str,))),
                    'preferred_worker': fake.uuid4(cast_to=None),
                    'sleep': fake.pybool(),
                    'sleep_at': fake.date_time(tzinfo=timezone.utc),
                    'title': fake.company(),
                },
                True,
            ),
            # Unexpected field case
            (
                {
                    'documentation': None,
                    'expires': fake.pybool(),
                    'expires_at': fake.date_time(tzinfo=timezone.utc),
                    'metadata': None,
                    'preferred_worker': None,
                    'sleep': fake.pybool(),
                    'sleep_at': fake.date_time(tzinfo=timezone.utc),
                    'title': fake.company(),
                    fake.slug().replace('-', '_'): fake.slug(),
                },
                False,
            ),
            # Missing data cases
            (
                {
                    'documentation': fake.url(),
                    'expires': fake.pybool(),
                    'expires_at': fake.date_time(tzinfo=timezone.utc),
                    'metadata': json.dumps(fake.pydict(value_types=(str,))),
                    'sleep': fake.pybool(),
                    'sleep_at': fake.date_time(tzinfo=timezone.utc),
                    'title': fake.company(),
                },
                False,
            ),
        )
        for payload, is_valid in cases:
            run_full_update_patch_test(api.simulations, simulation_factory, payload, is_valid)

    def test_create_from(self, api, simulation_factory, setup_mock_responses):
        def _run_test_case(payload, is_valid):
            endpoint_api = api.simulations

            if is_valid:
                expected_inst = simulation_factory(
                    endpoint_api.__api__, **{k: payload[k] for k in payload if k in ('title',)}
                )
                setup_mock_responses(
                    {
                        ('POST', join_urls(endpoint_api.url, endpoint_api.IMPORT_PATH)): {
                            'json': air_sdk.v2.endpoints.simulations.SimulationImportResponse(
                                id=expected_inst.id,
                                title=expected_inst.title,
                                organization=str(expected_inst.organization.__pk__),
                                organization_name=fake.slug(),
                            ),
                            'status_code': HTTPStatus.CREATED,
                        },
                        ('GET', join_urls(endpoint_api.url, str(expected_inst.__pk__))): {
                            'json': json.loads(expected_inst.json()),
                            'status_code': HTTPStatus.OK,
                        },
                    }
                )
                inst = endpoint_api.create_from(**payload)
                assert inst == expected_inst
                assert inst is not expected_inst
            else:
                with pytest.raises(Exception) as err:
                    endpoint_api.create_from(**payload)
                assert err.type in (TypeError, ValueError, json.JSONDecodeError, FileNotFoundError)

        fixtures_directory = Path(__file__).parent / 'fixtures' / 'create_from' / 'json'
        with (good_document_path := fixtures_directory / 'good_document.json').open(
            'r'
        ) as good_document_fd, (invalid_document_path := fixtures_directory / 'invalid_document.json').open(
            'r'
        ) as invalid_document_fd, (
            unexpected_document_path := fixtures_directory / 'unexpected_document.json'
        ).open('r') as unexpected_document_fd, tempfile.TemporaryDirectory() as temp_dir:
            cases = (
                # Empty Case
                ({}, False),
                # Minimal data case
                (
                    {
                        'title': fake.slug(),
                        'format': 'JSON',
                        'content': {},
                    },
                    True,
                ),
                # Explicit `organization=None`
                (
                    {
                        'title': fake.slug(),
                        'format': 'JSON',
                        'organization': None,
                        'content': {},
                    },
                    True,
                ),
                # Assigned organization
                (
                    {
                        'title': fake.slug(),
                        'format': 'JSON',
                        'organization': fake.slug(),
                        'content': {},
                    },
                    True,
                ),
                # Full dictionary content
                (
                    {
                        'title': fake.slug(),
                        'format': 'JSON',
                        'content': {
                            'oob': False,
                            'nodes': {'node-1': {'os': 'generic/ubuntu2204'}},
                            'links': [
                                [
                                    {'node': 'node-1', 'interface': 'eth1'},
                                    {'node': 'node-1', 'interface': 'eth2'},
                                ]
                            ],
                        },
                    },
                    True,
                ),
                # Valid string content
                (
                    {
                        'title': fake.slug(),
                        'format': 'JSON',
                        'content': '{}',
                    },
                    True,
                ),
                # Valid path content
                (
                    {
                        'title': fake.slug(),
                        'format': 'JSON',
                        'content': good_document_path,
                    },
                    True,
                ),
                # Valid file descriptor content
                (
                    {
                        'title': fake.slug(),
                        'format': 'JSON',
                        'content': good_document_fd,
                    },
                    True,
                ),
                # Invalid format
                (
                    {
                        'title': fake.slug(),
                        'format': 'NOT_JSON',
                        'content': {},
                    },
                    False,
                ),
                # Non-existent file at path
                (
                    {
                        'title': fake.slug(),
                        'format': 'JSON',
                        'content': Path(temp_dir) / 'non_existent_file',
                    },
                    False,
                ),
                # Invalid content (inline string)
                (
                    {
                        'title': fake.slug(),
                        'format': 'JSON',
                        'content': 'invalid content',
                    },
                    False,
                ),
                # Invalid content (path)
                (
                    {
                        'title': fake.slug(),
                        'format': 'JSON',
                        'content': invalid_document_path,
                    },
                    False,
                ),
                # Invalid content (file descriptor)
                (
                    {
                        'title': fake.slug(),
                        'format': 'JSON',
                        'content': invalid_document_fd,
                    },
                    False,
                ),
                # Unexpected content (inline string)
                (
                    {
                        'title': fake.slug(),
                        'format': 'JSON',
                        'content': '[]',
                    },
                    False,
                ),
                # Unexpected content (path)
                (
                    {
                        'title': fake.slug(),
                        'format': 'JSON',
                        'content': unexpected_document_path,
                    },
                    False,
                ),
                # Unexpected content (file descriptor)
                (
                    {
                        'title': fake.slug(),
                        'format': 'JSON',
                        'content': unexpected_document_fd,
                    },
                    False,
                ),
            )
            for payload, is_valid in cases:
                _run_test_case(payload, is_valid)

    @pytest.mark.parametrize(
        'format,image_ids',
        itertools.product(
            get_args(air_sdk.v2.endpoints.simulations.TopologyFormatType),
            (True, False),
        ),
    )
    def test_export(self, api, simulation_factory, setup_mock_responses, format, image_ids):
        endpoint_api = api.simulations
        expected_inst = simulation_factory(endpoint_api.__api__)
        non_existing_inst = simulation_factory(endpoint_api.__api__)

        def _run_test_case(payload, is_valid):
            if is_valid:
                setup_mock_responses(
                    {
                        (
                            'GET',
                            join_urls(
                                endpoint_api.url,
                                str(expected_inst.__pk__),
                                endpoint_api.EXPORT_PATH,
                            )
                            + f'?topology_format={format}&image_ids={str(image_ids).lower()}',
                        ): {
                            'json': air_sdk.v2.endpoints.simulations.TopologyFormat(
                                title=expected_inst.title,
                                format=format,
                                organization=str(expected_inst.organization.__pk__),
                                content=(content := {}),
                            ),
                            'status_code': HTTPStatus.OK,
                        },
                        (
                            'GET',
                            join_urls(
                                endpoint_api.url,
                                str(non_existing_inst.__pk__),
                                endpoint_api.EXPORT_PATH,
                            )
                            + f'?topology_format={format}&image_ids={str(image_ids).lower()}',
                        ): {
                            'json': {},
                            'status_code': HTTPStatus.NOT_FOUND,
                        },
                    }
                )
                inst = endpoint_api.export(**payload)
                assert inst == content
                assert inst is not content
            else:
                with pytest.raises(Exception) as err:
                    endpoint_api.export(**payload)
                assert err.type in (AirUnexpectedResponse,)

        query_params = {
            'format': format,
            'image_ids': image_ids,
        }
        cases = (
            # Export via instance
            (
                {
                    'simulation': expected_inst,
                    **query_params,
                },
                True,
            ),
            # Export via UUID
            (
                {
                    'simulation': UUID(expected_inst.__pk__),
                    **query_params,
                },
                True,
            ),
            # Export via string UUID
            (
                {
                    'simulation': str(expected_inst.__pk__),
                    **query_params,
                },
                True,
            ),
            # Non-existing simulation
            (
                {
                    'simulation': non_existing_inst.__pk__,
                    **query_params,
                },
                False,
            ),
        )
        for payload, is_valid in cases:
            _run_test_case(payload, is_valid)
