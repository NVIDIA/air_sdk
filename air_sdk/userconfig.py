# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
UserConfig model related module.
"""

import json
import os
from io import TextIOBase
from pathlib import Path
from typing import Dict, Optional, TextIO, Union

from .air_model import AirModel, AirModelAPI
from .exceptions import AirObjectDeleted
from .organization import Organization


class UserConfig(AirModel):
    """
    Manage a UserConfig.

    ### delete
    Delete the UserConfig. Once successful, the object should no longer be used and will raise
    `AirDeletedObject` when referenced.

    Raises:
    `AirUnexpectedResponse` - Delete failed

    ### json
    Returns a JSON string representation of the UserConfig.

    ### refresh
    Syncs the UserConfig with all values returned by the API

    ### update
    Update the UserConfig with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """

    KIND_CLOUD_INIT_USER_DATA = 'cloud-init-user-data'
    KIND_CLOUD_INIT_META_DATA = 'cloud-init-meta-data'
    VALID_KINDS = (KIND_CLOUD_INIT_USER_DATA, KIND_CLOUD_INIT_META_DATA)

    def __repr__(self):
        try:
            self_dict: Dict = json.loads(self.json())
            if self_dict.get('name', False) and self_dict.get('kind', False):
                return f'<UserConfig {self.name} {self.kind} {self.id}>'
        except AirObjectDeleted:
            pass

        return super().__repr__()


class UserConfigAPI(AirModelAPI[UserConfig]):
    """High-level interface for the UserConfig API."""

    API_VERSION = 2
    API_PATH = 'userconfigs'

    def create(
        self,
        name: str,
        kind: str,
        organization: Optional[Union[Organization, str]],
        content: Union[str, Path, TextIO],
    ) -> UserConfig:
        """
        Create a new UserConfig. Content data can be provided as a plain string, path to an existing file or an open file handle.
        Keep in mind that:
        - When passing a file path, it will be opened for reading using default encoding
        - When passing a file handle, it is assumed to be opened using a proper encoding and will be read from as-is
        - Due to a small size of UserConfig scripts, content will be loaded into memory in its entirety

        Arguments:
            name: UserConfig name
            kind: UserConfig kind, must be one of `UserConfig.VALID_KINDS`
            organization: Organization instance / ID to create the UserConfig in
            content: UserConfig data
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Raises:
        `AirUnexpectedResponse` - API did not return a 200 OK
            or valid response JSON
        `AttributeError` - provided content object is not one of the allowed types
        `FileNotFoundError` - when providing a path to a content file and the file is not present

        Example:
        ```
        >>> air.user_configs.create(name='my-config', kind=air.user_configs.model.KIND_CLOUD_INIT_USER_DATA, organization=my_org, content="my-content")
        <UserConfig my-config cloud-init-user-data 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        """

        if isinstance(content, str):
            if os.path.exists(content):
                with open(content, 'r') as content_file:
                    parsed_content = content_file.read()
            else:
                parsed_content = content
        elif isinstance(content, Path):
            with content.open('r') as content_file:
                parsed_content = content_file.read()
        elif isinstance(content, TextIOBase):
            parsed_content = content.read()
        else:
            raise AttributeError(f'Unexpected content type provided: `{type(content)}`')

        return super().create(
            name=name,
            kind=kind,
            organization=organization,
            content=parsed_content,
        )
