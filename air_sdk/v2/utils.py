# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
import inspect
from dataclasses import Field, fields, is_dataclass
from datetime import datetime, timezone
from functools import wraps
from typing import Optional, get_type_hints, TypeVar, Callable, Any, cast
from urllib.parse import ParseResult, urlparse
from uuid import UUID

from air_sdk.v2.typing import type_check

F = TypeVar('F', bound=Callable[..., Any])


def join_urls(*args: str) -> str:
    return '/'.join(frag.strip('/') for frag in args) + '/'


def iso_string_to_datetime(iso: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(iso.replace('Z', '+00:00'))
    except ValueError:
        return None


def datetime_to_iso_string(date: datetime) -> str:
    return date.astimezone(tz=timezone.utc).isoformat().replace('+00:00', 'Z')


def to_uuid(uuid: str) -> Optional[UUID]:
    try:
        return UUID(uuid, version=4)
    except ValueError:
        return None


def to_url(url: str) -> Optional[ParseResult]:
    try:
        parsed_url = urlparse(url)
        return parsed_url if all((parsed_url.scheme, parsed_url.netloc, parsed_url.path)) else None
    except AttributeError:
        return None


def is_dunder(name: str) -> bool:
    delimiter = '__'
    return name.startswith(delimiter) and name.endswith(delimiter)


def as_field(class_or_instance: object, name: str) -> Optional[Field]:  # type: ignore[type-arg]
    if is_dataclass(class_or_instance):
        try:
            return next(field for field in fields(class_or_instance) if field.name == name)
        except StopIteration:
            pass
    return None


def validate_payload_types(func: F) -> F:
    """A wrapper for validating the type of payload during create."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        hints = get_type_hints(func)

        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for name, value in bound_args.arguments.items():
            if name in hints:
                expected_type = hints[name]
                if not type_check(value, expected_type):
                    raise TypeError(f"Argument '{name}' must be {expected_type}, got {type(value)}")

        return func(*args, **kwargs)

    return cast(F, wrapper)
