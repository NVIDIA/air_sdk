# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
from http import HTTPStatus
from air_sdk.v2.endpoints.mixins import serialize_payload
from unittest.mock import patch, mock_open
from air_sdk.v2.utils import join_urls
from pathlib import Path
import pytest
import faker
import json
import random

faker.Faker.seed(0)
fake = faker.Faker()


class TestImageEndpointApi:
    def test_list(self, api, run_list_test, image_factory):
        run_list_test(api.images, image_factory)

    def test_refresh(self, api, run_refresh_test, image_factory):
        run_refresh_test(api.images, image_factory)

    def test_delete(self, api, image_factory, setup_mock_responses):
        # Create instance
        instance = image_factory(api.images.__api__)
        assert instance.__pk__ is not None, 'The instance must have a populated primary key.'
        # Set up mock client
        url = join_urls(api.images.url_v1, instance.__pk__)
        setup_mock_responses({('DELETE', url): {'status_code': HTTPStatus.NO_CONTENT}})
        # Call delete
        assert instance.delete() is None
        assert api.images.delete(instance.__pk__) is None

    @pytest.mark.parametrize(
        'payload,is_valid',
        (
            ({}, False),
            ({'name': None}, False),
            ({'cpu_arch': random.choice(('x86', 'ARM'))}, False),
            ({'name': fake.company()}, False),
            (
                {
                    'name': fake.company(),
                    'organization': fake.slug(),
                    'version': fake.slug(),
                    'default_username': fake.slug(),
                },
                False,
            ),
            (
                {
                    'name': fake.company(),
                    'organization': fake.uuid4(cast_to=str),
                    'version': fake.slug(),
                    'default_username': fake.slug(),
                    'default_password': fake.slug(),
                    'cpu_arch': random.choice(('x86', 'ARM')),
                    'base': fake.pybool(),
                    'agent_enabled': fake.pybool(),
                    'bios': None,
                    'bus': 'virtio',
                    'features': {},
                    'mountpoint': '',
                    'minimum_resources': {},
                    'notes': fake.text(max_nb_chars=64),
                    'provider': 'VM',
                    'release_notes': fake.text(max_nb_chars=64),
                    'user_manual': fake.url(),
                    'emulation_type': [],
                    'emulation_version': fake.slug(),
                    'console_support': {},
                },
                True,
            ),
            (
                {
                    'name': fake.company(),
                    'organization': fake.uuid4(cast_to=str),
                    'version': fake.slug(),
                    'default_username': fake.slug(),
                    'default_password': fake.slug(),
                    'cpu_arch': random.choice(('x86', 'ARM')),
                },
                True,
            ),
        ),
    )
    def test_create(self, api, image_factory, setup_mock_responses, payload, is_valid):
        """This tests that the data provided is properly validated and used."""

        if is_valid:
            processed_payload = json.loads(serialize_payload(payload))
            expected_inst = image_factory(api.images.__api__, **processed_payload)
            get_url = api.images.url + f'{expected_inst.id}/'
            setup_mock_responses(
                {
                    ('POST', api.images.url_v1): {
                        'json': json.loads(expected_inst.json()),
                        'status_code': HTTPStatus.CREATED,
                    },
                    ('GET', get_url): {
                        'json': json.loads(expected_inst.json()),
                        'status_code': HTTPStatus.OK,
                    },
                }
            )
            inst = api.images.create(**payload)
            assert inst == expected_inst
            assert inst is not expected_inst
        else:
            with pytest.raises(Exception) as err:
                api.images.create(**payload)
            assert err.type in (TypeError, ValueError)

    def test_update(self, mock_client, api, image_factory, setup_mock_responses):
        cases = (
            # Empty Case
            ({}, True),
            # None cases
            ({'name': None}, True),
            ({'organization': None}, True),
            ({'version': None}, True),
            ({'default_username': None}, True),
            ({'default_password': None}, True),
            ({'cpu_arch': None}, True),
            # Valid payload cases
            ({'name': fake.company()}, True),
            ({'organization': fake.uuid4(cast_to=str)}, True),
            ({'version': fake.slug()}, True),
            ({'default_username': fake.slug()}, True),
            ({'default_password': fake.slug()}, True),
            ({'cpu_arch': 'x86'}, True),
            # Invalid values cases
            ({'name': 1}, False),
            ({'organization': fake.pyint()}, False),
            ({'cpu_arch': fake.pyint()}, False),
            ({'default_username': fake.pyint()}, False),
            ({'default_password': fake.pyint()}, False),
        )

        for payload, is_valid in cases:
            instance = image_factory(api.images.__api__)
            if is_valid:
                processed_payload = json.loads(
                    serialize_payload({k: v for k, v in payload.items() if v is not None})
                )
                updated_inst = image_factory(api.images.__api__, **{**instance.dict(), **processed_payload})
                detail_url = join_urls(api.images.url_v1, str(instance.__pk__))
                get_url = join_urls(api.images.url, str(instance.__pk__))
                current_img = 'IMG'
                desired_img = 'IMG_CHANGED'

                def _img_refresh(*args, **kwargs):
                    nonlocal current_img
                    current_img = desired_img
                    return json.loads(instance.json())

                mock_client.register_uri(
                    'GET',
                    get_url,
                    json=_img_refresh,
                    status_code=HTTPStatus.OK,
                )

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
                assert current_img == desired_img
            else:
                with pytest.raises(Exception) as err:
                    instance.update(**payload)
                assert err.type in (TypeError, ValueError)

    def test_full_update(self, mock_client, api, image_factory, setup_mock_responses):
        cases = (
            # Empty Case
            ({}, False),
            (
                {
                    'name': fake.company(),
                    'organization': fake.uuid4(cast_to=str),
                    'version': fake.slug(),
                    'default_username': fake.slug(),
                    'default_password': fake.slug(),
                    'cpu_arch': random.choice(('x86', 'ARM')),
                },
                True,
            ),
        )
        for payload, is_valid in cases:
            instance = image_factory(api.images.__api__)
            if is_valid:
                processed_payload = json.loads(serialize_payload(payload))
                updated_inst = image_factory(api.images.__api__, **{**instance.dict(), **processed_payload})
                detail_url = join_urls(api.images.url_v1, str(instance.__pk__))
                get_url = join_urls(api.images.url, str(instance.__pk__))
                current_img = 'IMG'
                desired_img = 'IMG_CHANGED'

                def _img_refresh(*args, **kwargs):
                    nonlocal current_img
                    current_img = desired_img
                    return json.loads(instance.json())

                mock_client.register_uri(
                    'GET',
                    get_url,
                    json=_img_refresh,
                    status_code=HTTPStatus.OK,
                )

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
                assert current_img == desired_img
            else:
                with pytest.raises(Exception) as err:
                    instance.full_update(**payload)
                assert err.type in (TypeError, ValueError)

    def test_publish(self, mock_client, api, image_factory, setup_mock_responses):
        instance = image_factory(api.images.__api__)
        url = join_urls(api.images.url_v1, str(instance.__pk__), '/publish/')
        get_url = join_urls(api.images.url, str(instance.__pk__))
        current_img = 'IMG'
        desired_img = 'IMG_CHANGED'

        def _img_refresh(*args, **kwargs):
            nonlocal current_img
            current_img = desired_img
            return json.loads(instance.json())

        mock_client.register_uri(
            'GET',
            get_url,
            json=_img_refresh,
            status_code=HTTPStatus.OK,
        )
        setup_mock_responses(
            {
                ('PUT', url): {
                    'status_code': HTTPStatus.NO_CONTENT,
                },
            }
        )
        contact = fake.email(domain='nvidia.com')
        assert instance.publish(contact) is None
        assert current_img == desired_img

    def test_unpublish(self, mock_client, api, image_factory, setup_mock_responses):
        instance = image_factory(api.images.__api__)
        url = join_urls(api.images.url_v1, str(instance.__pk__), '/publish/')
        get_url = join_urls(api.images.url, str(instance.__pk__))
        current_img = 'IMG'
        desired_img = 'IMG_CHANGED'

        def _img_refresh(*args, **kwargs):
            nonlocal current_img
            current_img = desired_img
            return json.loads(instance.json())

        mock_client.register_uri(
            'GET',
            get_url,
            json=_img_refresh,
            status_code=HTTPStatus.OK,
        )

        setup_mock_responses(
            {
                ('DELETE', url): {
                    'status_code': HTTPStatus.NO_CONTENT,
                },
            }
        )

        assert instance.unpublish() is None
        assert current_img == desired_img

    @patch.object(Path, 'open', new_callable=mock_open, read_data=b'fake_image_data')
    @patch('air_sdk.v2.endpoints.images.Image.__refresh__', autospec=True)
    def test_upload(self, mock_refresh, mock_file, api, image_factory, setup_mock_responses):
        mock_refresh.return_value = None
        instance = image_factory(api.images.__api__)
        url = join_urls(api.images.url_v1, str(instance.__pk__), '/upload/')
        setup_mock_responses(
            {
                ('PUT', url): {
                    'status_code': HTTPStatus.NO_CONTENT,
                },
            }
        )
        filepath = 'fake_image.jpg'
        assert instance.upload(filepath) is None
        mock_file.assert_called_once_with('rb')
