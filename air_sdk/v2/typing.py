# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
import inspect
from typing import Any, List, Literal, Optional, Tuple, Type, TypeVar, Union, get_args, get_origin
import sys
from dataclasses import is_dataclass
from typing import (
    ForwardRef,
)

T = TypeVar('T')


def union_args_are_optional(args: Tuple[Union[Any, Any], ...]) -> bool:
    return len(args) >= 2 and type(None) in args


def is_union(type_: Type[Any]) -> bool:
    return get_origin(type_) == Union


def is_optional_union(type_: Type[Any]) -> bool:
    return is_union(type_) and union_args_are_optional(get_args(type_))


def get_optional_arg(optional_type: Type[Optional[T]]) -> Type[T]:
    return next(arg for arg in get_args(optional_type) if arg is not type(None))  # type: ignore[no-any-return]


def get_list_arg(list_type: Type[List[T]]) -> Type[T]:
    return get_args(list_type)[0]  # type: ignore[no-any-return]


def is_typed_dict(expected_type: Type[Any]) -> bool:
    """Determine if the `expected_type` provided is a subclass of TypedDict."""
    return hasattr(expected_type, '__annotations__') and not is_dataclass(expected_type)


def type_check_typed_dict(value: Any, expected_type: Type[Any]) -> bool:
    """Perform type checking when the expected_type is a subclass of TypedDict.

    This currently does not work if the expected_type is also a dataclass.
    """
    if not isinstance(value, dict):
        return False
    expected_keys = expected_type.__annotations__.keys()
    # Check all keys provided are defined within the expected_type TypedDict
    if not all(key in value for key in expected_keys):
        return False
    # Recursively check each key's value type
    return all(type_check(value[key], expected_type.__annotations__[key]) for key in expected_keys)


def type_check(value: Any, expected_type: Type[Any]) -> bool:
    """Recursively check if the value matches the expected type."""
    from air_sdk.v2.air_model import PrimaryKey  # noqa

    if isinstance(expected_type, ForwardRef):
        if sys.version_info >= (3, 9):  # Python 3.9+ requires a third `recursive_guard` arg
            expected_type = expected_type._evaluate(globals(), locals(), frozenset())
        else:
            expected_type = expected_type._evaluate(globals(), locals())
    origin = get_origin(expected_type)
    args = get_args(expected_type)

    if origin is None:  # Base case
        if is_typed_dict(expected_type):
            return type_check_typed_dict(value, expected_type)
        if expected_type == Any:
            return True
        return isinstance(value, expected_type)

    if origin is Union:
        return any(type_check(value, arg) for arg in args)

    if origin is list:
        if not isinstance(value, list):
            return False
        if not args:  # We're already a list, so if not args then we're good
            return True
        return all(type_check(item, args[0]) for item in value)

    if origin is dict:
        if not isinstance(value, dict):
            return False
        if not args:  # We're already a dict, so if no args then we're good
            return True
        key_type, value_type = args
        return all(type_check(k, key_type) and type_check(v, value_type) for k, v in value.items())

    if origin is Literal:
        return any(value == arg for arg in args)

    if inspect.isclass(origin):
        return isinstance(value, origin)

    return False
