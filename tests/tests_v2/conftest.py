# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
import json
from datetime import timezone
from http import HTTPStatus
import random
from typing import Any, TypedDict, Optional, List, Dict

import pytest
import requests_mock
import faker

from air_sdk import v2
from air_sdk.v2 import AirError
from air_sdk.v2.air_model import AirModel
from air_sdk.v2.endpoints.mixins import serialize_payload
from air_sdk.v2.utils import join_urls

faker.Faker.seed(0)
fake = faker.Faker()


@pytest.fixture
def api():
    return v2.AirApi(api_url='https://air-fake-test.nvidia.com/api/', authenticate=False)


@pytest.fixture
def mock_client():
    """Set up a mock client for making requests."""
    with requests_mock.Mocker() as m:
        yield m


class PaginatedResponseData(TypedDict):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[Dict[str, Any]]


class PaginatedResponse(TypedDict):
    json: PaginatedResponseData
    status_code: int


@pytest.fixture
def paginated_response() -> PaginatedResponse:
    return {'json': {'next': None, 'previous': None, 'count': 0, 'results': []}, 'status_code': HTTPStatus.OK}


@pytest.fixture
def setup_mock_responses(mock_client):
    """Register responses for the mock client.""

    We can use this to handle mocking at the `requests` library level.
    """

    def _setup_mock_responses(responses):
        for (method, url), response in responses.items():
            mock_client.register_uri(
                method, url, json=response.get('json'), status_code=response.get('status_code', HTTPStatus.OK)
            )

    return _setup_mock_responses


# FACTORY CLASSES


@pytest.fixture
def account_factory():
    def _account_factory(api, **kwargs: Any):
        defaults = {'id': fake.uuid4(cast_to=str)}
        return api.accounts.load_model({**defaults, **kwargs})

    return _account_factory


@pytest.fixture
def api_token_factory():
    def _api_token_factory(api, **kwargs: Any):
        expiry = fake.date_time(tzinfo=timezone.utc)
        defaults = {
            'id': fake.uuid4(cast_to=str),
            'name': fake.slug(),
            'created': fake.date_time(end_datetime=expiry, tzinfo=timezone.utc),
            'expiry': expiry,
        }
        return api.api_tokens.load_model({**defaults, **kwargs})

    return _api_token_factory


@pytest.fixture
def announcement_factory():
    def _announcement_factory(api, **kwargs: Any):
        modified = fake.date_time(tzinfo=timezone.utc)
        defaults = {
            'id': fake.uuid4(cast_to=str),
            'severity': random.choice(('Alert', 'Info')),
            'created': fake.date_time(end_datetime=modified, tzinfo=timezone.utc),
            'modified': modified,
            'message': fake.text(),
        }
        return api.announcements.load_model({**defaults, **kwargs})

    return _announcement_factory


@pytest.fixture
def image_factory():
    def _image_factory(api, **kwargs: Any):
        modified = fake.date_time(tzinfo=timezone.utc)
        defaults = {
            'id': fake.uuid4(cast_to=str),
            'agent_enabled': fake.pybool(),
            'archived': fake.pybool(),
            'bios': None,
            'bus': 'virtio',
            'cpu_arch': random.choice(('x86', 'ARM')),
            'created': fake.date_time(end_datetime=modified, tzinfo=timezone.utc),
            'default_username': fake.slug(),
            'default_password': fake.slug(),
            'features': {},
            'modified': modified,
            'mountpoint': '',
            'console_support': {'serial': False, 'visual': False, 'default': None},
            'minimum_resources': {'cpu': 1, 'memory': 1024, 'storage': 10},
            'name': fake.company(),
            'notes': fake.text(max_nb_chars=64),
            'organization': fake.uuid4(cast_to=str),
            'published': fake.pybool(),
            'provider': random.choice(('VM', 'CONTAINER')),
            'release_notes': fake.text(max_nb_chars=64),
            'simx': None,
            'size': fake.pyint(10000, 20000),
            'upload_status': 'COMPLETE',
            'uploader': fake.uuid4(cast_to=str),
            'user_manual': fake.url(),
            'version': fake.slug(),
            'can_edit': fake.pybool(),
            'organization_name': fake.company(),
            'uploader_username': fake.email(domain='nvidia.com'),
        }
        return api.images.load_model({**defaults, **kwargs})

    return _image_factory


@pytest.fixture
def node_factory():
    def _node_factory(api, **kwargs: Any):
        modified = fake.date_time(tzinfo=timezone.utc)
        defaults = {
            'id': fake.uuid4(cast_to=str),
            'name': fake.slug(),
            'created': fake.date_time(end_datetime=modified, tzinfo=timezone.utc),
            'modified': modified,
            'simulation': fake.uuid4(cast_to=str),
            'os': fake.uuid4(cast_to=str),
            'console_port': fake.port_number(),
            'serial_port': fake.port_number(),
            'state': random.choice(('RUNNING', 'PAUSED', 'SHUTOFF', 'SNAPSHOT')),
            'memory': fake.pyint(1024, 2048),
            'storage': fake.pyint(8, 16),
            'cpu': fake.pyint(1, 4),
            'version': 3,
            'features': '{}',
            'boot_group': fake.pyint(10, 100),
            'pos_x': fake.pyfloat(min_value=-10, max_value=10),
            'pos_y': fake.pyfloat(min_value=-10, max_value=10),
        }
        for key, value in list(kwargs.items()):
            if key in ('cpu', 'memory', 'storage') and value is None:
                del kwargs[key]  # These will be populated with defaults by the BE
        return api.nodes.load_model({**defaults, **kwargs})

    return _node_factory


@pytest.fixture
def cloud_init_factory():
    def _cloud_init_factory(api, **kwargs: Any):
        defaults = {
            'simulation_node': fake.uuid4(),
            'user_data': fake.uuid4(),
            'meta_data': fake.uuid4(),
            'user_data_name': fake.slug(),
            'meta_data_name': fake.slug(),
        }
        return api.cloud_inits.load_model({**defaults, **kwargs})

    return _cloud_init_factory


@pytest.fixture
def interface_factory():
    def _interface_factory(api, **kwargs: Any):
        defaults = {
            'id': fake.uuid4(cast_to=str),
            'name': fake.slug(),
            'link_up': fake.pybool(),
            'internal_ipv4': fake.ipv4(),
            'full_ipv6': fake.ipv6(),
            'prefix_ipv6': fake.ipv6(),
            'interface_type': random.choice(('ETH_INTF', 'PCIE_INTF', 'OOB_INTF')),
            'port_number': fake.port_number(),
            'preserve_mac': fake.pybool(),
            'outbound': fake.pybool(),
            'mac_address': fake.mac_address(),
            'node': fake.uuid4(cast_to=str),
            'simulation': fake.uuid4(cast_to=str),
            'link': None,
        }
        return api.interfaces.load_model({**defaults, **kwargs})

    return _interface_factory


@pytest.fixture
def job_factory():
    def _job_factory(api, **kwargs):
        last_updated = fake.date_time(tzinfo=timezone.utc)
        defaults = {
            'id': fake.uuid4(cast_to=str),
            'category': random.choice(('START', 'STOP', 'EXEC', 'PURGE')),
            'state': random.choice(('CREATED', 'QUEUED', 'WORKING', 'COMPLETE', 'FAILED', 'CANCELLED')),
            'created': fake.date_time(end_datetime=last_updated, tzinfo=timezone.utc),
            'last_updated': last_updated,
            'notes': fake.text(),
            'data': fake.text(),
            'simulation': fake.uuid4(cast_to=str),
            'worker': fake.uuid4(cast_to=str),
        }
        return api.jobs.load_model({**defaults, **kwargs})

    return _job_factory


@pytest.fixture
def link_factory():
    def _link_factory(api, **kwargs):
        defaults = {
            'id': fake.uuid4(cast_to=str),
            'simulation_interfaces': [fake.uuid4(cast_to=str), fake.uuid4(cast_to=str)],
        }
        return api.links.load_model({**defaults, **kwargs})

    return _link_factory


@pytest.fixture
def marketplace_demo_factory():
    """A factory fixture for generating valid marketplace demos."""

    def _marketplace_demo_factory(api, **kwargs: Any):
        """A factory class for generating MarketplaceDemos."""
        modified = fake.date_time(tzinfo=timezone.utc)
        defaults = {
            'modified': modified,
            'created': fake.date_time(end_datetime=modified, tzinfo=timezone.utc),
            'description': fake.text(),
            'documentation': fake.url(),
            'documentation_details': fake.text(),
            'icon': fake.slug(),
            'id': fake.uuid4(cast_to=str),
            'liked_by_account': fake.pybool(),
            'like_count': fake.pyint(),
            'name': fake.company(),
            'owner_email': (
                fake.slug()  # To prevent real emails
                + fake.email(domain='nvidia.com')
            ),
            'published': fake.pybool(),
            'repo': fake.url(),
            'snapshot': fake.uuid4(cast_to=str),
            'tags': fake.pylist(value_types=(str,)),
        }
        return api.marketplace_demos.load_model({**defaults, **kwargs})

    return _marketplace_demo_factory


@pytest.fixture
def marketplace_demo_tag_factory():
    """A factory fixture for generating valid marketplace demo tags."""

    def _marketplace_demo_tag_factory(api, **kwargs: Any):
        """A factory class for generating MarketplaceDemos."""
        defaults = {'name': fake.slug()}
        return api.marketplace_demo_tags.load_model({**defaults, **kwargs})

    return _marketplace_demo_tag_factory


@pytest.fixture
def resource_budget_factory():
    def _resource_budget_factory(api, **kwargs: Any):
        defaults = {
            'id': fake.uuid4(cast_to=str),
            'cpu': fake.pyint(),
            'cpu_used': 0,
            'image_uploads': fake.pyint(),
            'image_uploads_used': 0,
            'memory': fake.pyint(),
            'memory_used': 0,
            'simulations': fake.pyint(),
            'simulations_used': 0,
            'storage': fake.pyint(),
            'storage_used': 0,
            'userconfigs': fake.pyint(),
            'userconfigs_used': 0,
        }
        return api.resource_budgets.load_model({**defaults, **kwargs})

    return _resource_budget_factory


@pytest.fixture
def organization_factory(resource_budget_factory):
    def _organization_factory(api, **kwargs: Any):
        defaults = {
            'id': fake.uuid4(cast_to=str),
            'name': fake.company(),
            'member_count': fake.pyint(),
            'resource_budget': resource_budget_factory(api),
        }
        return api.organizations.load_model({**defaults, **kwargs})

    return _organization_factory


@pytest.fixture
def service_factory():
    def _service_factory(api, **kwargs: Any):
        modified = fake.date_time(tzinfo=timezone.utc)
        defaults = {
            'id': fake.uuid4(cast_to=str),
            'name': fake.slug(),
            'created': fake.date_time(end_datetime=modified, tzinfo=timezone.utc),
            'modified': modified,
            'src_port': fake.port_number(),
            'dest_port': fake.port_number(),
            'interface': fake.uuid4(cast_to=str),
            'simulation': fake.uuid4(cast_to=str),
            'service_type': random.choice(('SSH', 'HTTPS', 'HTTP')),
            'host': fake.domain_name(),
        }
        return api.services.load_model({**defaults, **kwargs})

    return _service_factory


@pytest.fixture
def simulation_factory():
    def _simulation_factory(api, **kwargs: Any):
        expires_at = sleep_at = fake.date_time(tzinfo=timezone.utc)
        modified = fake.date_time(end_datetime=expires_at, tzinfo=timezone.utc)
        defaults = {
            'id': fake.uuid4(cast_to=str),
            'title': fake.slug(),
            'state': random.choice(('NEW', 'LOADING', 'LOADED', 'ERROR')),
            'sleep': True,
            'owner': fake.email(),
            'cloned': False,
            'expires': True,
            'modified': modified,
            'created': fake.date_time(end_datetime=modified, tzinfo=timezone.utc),
            'sleep_at': sleep_at,
            'expires_at': expires_at,
            'organization': fake.uuid4(cast_to=str),
            'documentation': fake.url(),
            'write_ok': fake.pybool(),
            'metadata': json.dumps(fake.pydict(value_types=[str])),
        }
        return api.simulations.load_model({**defaults, **kwargs})

    return _simulation_factory


@pytest.fixture
def system_factory():
    def _system_factory(api, **kwargs: Any):
        defaults = {'id': fake.uuid4(cast_to=str)}
        return api.systems.load_model({**defaults, **kwargs})

    return _system_factory


@pytest.fixture
def user_config_factory():
    def _user_config_factory(api, **kwargs: Any):
        defaults = {
            'id': fake.uuid4(cast_to=str),
            'name': fake.slug(),
            'owner': fake.uuid4(cast_to=str),  # An account
            'owner_budget': fake.uuid4(cast_to=str),
            'kind': random.choice(('cloud-init-user-data', 'cloud-init-meta-data')),
            'organization': fake.uuid4(cast_to=str),
            'organization_budget': fake.uuid4(cast_to=str),
            'content': fake.text(),
        }
        return api.user_configs.load_model({**defaults, **kwargs})

    return _user_config_factory


@pytest.fixture
def worker_factory():
    def _worker_factory(api, **kwargs: Any):
        modified = fake.date_time(tzinfo=timezone.utc)
        defaults = {
            'id': fake.uuid4(cast_to=str),
            'created': fake.date_time(end_datetime=modified, tzinfo=timezone.utc),
            'modified': modified,
            'available': True,
            'capabilities': '["general"]',
            'cpu': fake.pyint(),
            'cpu_arch': random.choice(('x86', 'ARM')),
            'contact': fake.email(),
            'fleet': fake.uuid4(cast_to=str),
            'fqdn': fake.domain_name(),
            'gpu': fake.pyint(),
            'ip_address': fake.ipv4(),
            'memory': fake.pyint(),
            'port_range': '10000-30000',
            'registered': True,
            'storage': fake.pyint(),
            'tunnel_port': fake.port_number(),
            'vgpu': fake.pyint(),
        }
        return api.workers.load_model({**defaults, **kwargs})

    return _worker_factory


# COMMON TEST CASES


@pytest.fixture
def run_list_test(setup_mock_responses):
    """A pytest fixture for running a common test on the `list` method of an api."""

    def _run_list_test(endpoint_api, model_factory):
        # Set up mock client
        results = [
            json.loads(model_factory(endpoint_api.__api__).json()),
            json.loads(model_factory(endpoint_api.__api__).json()),
        ]
        setup_mock_responses(
            {
                ('GET', endpoint_api.url): {
                    'json': {'previous': None, 'next': None, 'count': len(results), 'results': results},
                    'status_code': HTTPStatus.OK,
                }
            }
        )
        # Test SDK
        instances = list(endpoint_api.list(limit=len(results)))
        assert len(instances) == len(results)
        assert isinstance(instances[0], endpoint_api.model)
        return instances

    return _run_list_test


@pytest.fixture
def run_refresh_test(setup_mock_responses):
    def _run_refresh_test(endpoint_api, model_factory):
        instance = model_factory(endpoint_api.__api__)
        model_data = json.loads(instance.json())
        setup_mock_responses(
            {
                ('GET', join_urls(endpoint_api.url, str(instance.__pk__))): {
                    'json': model_data,
                    'status_code': HTTPStatus.OK,
                }
            }
        )
        instance.refresh()

    return _run_refresh_test


@pytest.fixture
def run_delete_test(setup_mock_responses):
    """A pytest fixture for running a common test on the `delete` method of an api."""

    def _run_delete_test(endpoint_api, model_factory):
        # Create instance
        instance = model_factory(endpoint_api.__api__)
        assert instance.__pk__ is not None, 'The instance must have a populated primary key.'
        # Set up mock client
        url = join_urls(endpoint_api.url, instance.__pk__)
        setup_mock_responses({('DELETE', url): {'status_code': HTTPStatus.NO_CONTENT}})
        # Call delete
        assert instance.delete() is None
        assert instance.__pk__ is None
        with pytest.raises(AirError):
            instance.delete()

    return _run_delete_test


@pytest.fixture
def run_create_test_case(setup_mock_responses):
    """A pytest fixture for testing if the provided payload is valid for the endpoint api."""

    def _run_test_case(endpoint_api, model_factory, payload, is_valid):
        if is_valid:
            processed_payload = json.loads(serialize_payload(payload))
            expected_inst = model_factory(endpoint_api.__api__, **processed_payload)
            setup_mock_responses(
                {
                    ('POST', endpoint_api.url): {
                        'json': json.loads(expected_inst.json()),
                        'status_code': HTTPStatus.CREATED,
                    }
                }
            )
            inst = endpoint_api.create(**payload)
            assert inst == expected_inst
            assert inst is not expected_inst
        else:
            with pytest.raises(Exception) as err:
                endpoint_api.create(**payload)
            assert err.type in (TypeError, ValueError)

    return _run_test_case


@pytest.fixture
def run_update_patch_test(setup_mock_responses):
    def _run_test_case(endpoint_api, model_factory, payload, is_valid):
        instance = model_factory(endpoint_api.__api__)
        if is_valid:
            processed_payload = json.loads(
                serialize_payload({k: v for k, v in payload.items() if v is not None})
            )
            updated_inst = model_factory(endpoint_api.__api__, **{**instance.dict(), **processed_payload})
            detail_url = join_urls(endpoint_api.url, str(instance.__pk__))
            setup_mock_responses(
                {
                    ('PATCH', detail_url): {
                        'json': json.loads(instance.json()),
                        'status_code': HTTPStatus.OK,
                    },
                }
            )
            instance.update(**payload)
            assert instance == updated_inst
            assert instance is not updated_inst
        else:
            with pytest.raises(Exception) as err:
                instance.update(**payload)
            assert err.type in (TypeError, ValueError)

    return _run_test_case


@pytest.fixture
def run_full_update_patch_test(setup_mock_responses):
    def _run_test_case(endpoint_api, model_factory, payload, is_valid):
        instance = model_factory(endpoint_api.__api__)
        if is_valid:
            processed_payload = json.loads(serialize_payload(payload))
            updated_inst = model_factory(endpoint_api.__api__, **{**instance.dict(), **processed_payload})
            detail_url = join_urls(endpoint_api.url, str(instance.__pk__))
            setup_mock_responses(
                {
                    ('PATCH', detail_url): {
                        'json': json.loads(instance.json()),
                        'status_code': HTTPStatus.OK,
                    },
                }
            )
            instance.full_update(**payload)
            assert instance == updated_inst
            assert instance is not updated_inst
        else:
            with pytest.raises(Exception) as err:
                instance.full_update(**payload)
            assert err.type in (TypeError, ValueError)

    return _run_test_case


@pytest.fixture
def run_full_update_put_test(setup_mock_responses):
    def _run_test_case(endpoint_api, model_factory, payload, is_valid):
        instance = model_factory(endpoint_api.__api__)
        if is_valid:
            processed_payload = json.loads(serialize_payload(payload))
            updated_inst = model_factory(endpoint_api.__api__, **{**instance.dict(), **processed_payload})
            detail_url = join_urls(endpoint_api.url, str(instance.__pk__))
            setup_mock_responses(
                {
                    ('PUT', detail_url): {
                        'json': json.loads(instance.json()),
                        'status_code': HTTPStatus.OK,
                    },
                }
            )
            instance.full_update(**payload)
            assert instance == updated_inst
            assert instance is not updated_inst
        else:
            with pytest.raises(Exception) as err:
                instance.full_update(**payload)
            assert err.type in (TypeError, ValueError)

    return _run_test_case


@pytest.fixture
def run_api_not_implemented_test(api):
    def _run_test_case(model_cls, model_factory):
        instance = model_factory(api)
        assert issubclass(model_cls, AirModel)
        assert isinstance(instance, model_cls)
        assert isinstance(instance.dict(), dict)
        assert isinstance(instance.json(), str)
        assert instance.__pk__ is not None
        assert str(instance.id) == str(instance.__pk__)
        with pytest.raises(NotImplementedError):
            instance.refresh()

    return _run_test_case
