# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT


from datetime import datetime
from json import JSONEncoder
from typing import Any
from uuid import UUID

from air_sdk.v2.utils import datetime_to_iso_string


class AirJSONEncoder(JSONEncoder):
    """`JSONEncoder` with Air-specific decoding logic."""

    def default(self, o: Any) -> Any:
        """`JSONEncoder.default` with ability to decode `datetime` and UUID objects."""
        from air_sdk.v2.air_model import AirModel

        if isinstance(o, datetime):
            return datetime_to_iso_string(o)
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, AirModel):
            pk = getattr(o, '__pk__', None)
            if pk is None:
                raise ValueError(
                    f'The `{o.__class__.__name__}` provided is not JSON serializable: __pk__ is None'
                )
            return str(pk)
        return super().default(o)
