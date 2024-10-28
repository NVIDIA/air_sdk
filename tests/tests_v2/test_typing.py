# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

import pytest
from typing import TypedDict, Union, List, Dict
from dataclasses import dataclass
from air_sdk.v2 import typing

import faker

faker.Faker.seed(0)
fake = faker.Faker()


class ExampleTypedDict(TypedDict):
    field1: int
    field2: str


class NestedTypedDict(TypedDict):
    field1: ExampleTypedDict
    field2: List[str]


@dataclass
class ExampleDataclass:
    field1: int
    field2: str


class TestTypingMethods:
    @pytest.mark.parametrize(
        'test_type,expected',
        [
            (ExampleTypedDict, True),
            (ExampleDataclass, False),
            (int, False),
        ],
    )
    def test_is_typed_dict(self, test_type, expected):
        assert typing.is_typed_dict(test_type) == expected

    @pytest.mark.parametrize(
        'value,expected',
        [
            ({'field1': fake.pyint(), 'field2': fake.slug()}, True),
            ({'field1': fake.pyint()}, False),
            ({'field1': str(fake.pyint()), 'field2': fake.slug()}, False),
        ],
    )
    def test_type_check_typed_dict(self, value, expected):
        assert typing.type_check_typed_dict(value, ExampleTypedDict) == expected

    @pytest.mark.parametrize(
        'value,expected',
        [
            (
                {
                    'field1': {'field1': fake.pyint(), 'field2': fake.slug()},
                    'field2': [fake.slug(), fake.slug()],
                },
                True,
            ),
            (
                {
                    'field1': {'field1': fake.pyint(), 'field2': fake.pyint()},
                    'field2': [fake.slug(), fake.slug()],
                },
                False,
            ),
        ],
    )
    def test_type_check_typed_dict_nested(self, value, expected):
        assert typing.type_check(value, NestedTypedDict) == expected

    @pytest.mark.parametrize(
        'value,expected',
        [
            ([1, 2, 3], True),
            ([1, 2, 'three'], False),
        ],
    )
    def test_type_check_list(self, value, expected):
        assert typing.type_check(value, List[int]) == expected

    @pytest.mark.parametrize(
        'value,expected',
        [
            (123, True),
            (fake.slug(), True),
            (123.45, False),
        ],
    )
    def test_type_check_union(self, value, expected):
        assert typing.type_check(value, Union[int, str]) == expected

    @pytest.mark.parametrize(
        'value,expected',
        [
            ({'key': 'value'}, True),
            ({1: 'value'}, False),
        ],
    )
    def test_type_check_dict(self, value, expected):
        assert typing.type_check(value, Dict[str, str]) == expected
