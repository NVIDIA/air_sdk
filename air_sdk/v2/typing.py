# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
import inspect
from typing import Any, Optional, Tuple, Type, TypeVar, Union, get_args, get_origin, List

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


def type_check(value: Any, expected_type: Type[Any]) -> bool:
    """Recursively check if the value matches the expected type."""
    origin = get_origin(expected_type)
    args = get_args(expected_type)

    if origin is None:  # Base case
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

    if inspect.isclass(origin):
        return isinstance(value, origin)

    return False
