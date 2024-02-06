# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Image module
"""

from . import util
from .air_model import AirModel
from .logger import air_sdk_logger as logger



class Image(AirModel):
    """
    Manage an Image

    ### delete
    Delete the image. Once successful, the object should no longer be used and will raise
    [`AirDeletedObject`](/docs/exceptions) when referenced.

    Raises:
    [`AirUnexpectedResposne`](/docs/exceptions) - Delete failed

    ### json
    Returns a JSON string representation of the image

    ### refresh
    Syncs the image with all values returned by the API

    ### update
    Update the image with the provided data

    Arguments:
        kwargs (dict, optional): All optional keyword arguments are applied as key/value
                pairs in the request's JSON payload
    """

    def copy(self, organization):
        """
        Make a copy of the image in another organization

        Arguments:
            organization (str | `Organization`): `Organization` or ID

        Returns:
        [`Image`](/docs/image)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - Copy failed

        Example:
        ```
        >>> image = air.images.get('33d8a377-ef0a-4a0d-ac2a-076e32678e18')
        >>> target_org = air.organizations.get('b0e47509-4099-4e24-b96f-d1278d431f46')
        >>> image.copy(target_org)
        <Image cumulus-vx-5.4.0 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self._api.url}{self.id}/copy/'
        res = self._api.client.post(url, json={'organization': organization})
        util.raise_if_invalid_response(res, status_code=201)
        return Image(self._api, **res.json())

    def upload(self, filename):
        """
        Upload an image file

        Arguments:
            filename (str): Absolute path to the local image

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - Upload failed
        """
        url = f'{self._api.url}{self.id}/upload/'
        with open(filename, 'rb') as image_file:
            res = self._api.client.put(url, data=image_file)
        util.raise_if_invalid_response(res, status_code=204, data_type=None)

    def __repr__(self):
        if self._deleted or not self.name:
            return super().__repr__()
        return f'<Image {self.name} {self.id}>'


class ImageApi:
    """High-level interface for the Image API"""

    def __init__(self, client):
        self.client = client
        self.url = self.client.api_url + '/image/'

    def get(self, image_id, **kwargs):
        """
        Get an existing image

        Arguments:
            image_id (str): Image ID
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        [`Image`](/docs/image)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.images.get('3dadd54d-583c-432e-9383-a2b0b1d7f551')
        <Image cumulus-vx-4.2.1 3dadd54d-583c-432e-9383-a2b0b1d7f551>
        ```
        """
        url = f'{self.url}{image_id}/'
        res = self.client.get(url, params=kwargs)
        util.raise_if_invalid_response(res)
        return Image(self, **res.json())

    def list(self, **kwargs):
        # pylint: disable=line-too-long
        """
        List existing images

        Arguments:
            kwargs (dict, optional): All other optional keyword arguments are applied as query
                parameters/filters

        Returns:
        list

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> air.images.list()
        [<Image cumulus-vx-4.2.1 c51b49b6-94a7-4c93-950c-e7fa4883591>, <Image generic/ubuntu18.04 3134711d-015e-49fb-a6ca-68248a8d4aff>]
        ```
        """  # pylint: enable=line-too-long
        res = self.client.get(f'{self.url}', params=kwargs)
        util.raise_if_invalid_response(res, data_type=list)
        return [Image(self, **image) for image in res.json()]

    @util.required_kwargs(
        ['name', 'organization', 'version', 'default_username', 'default_password', 'cpu_arch']
    )
    def create(self, **kwargs):
        """
        Create a new image

        Arguments:
            name (str): Image name
            organization (str | `Organization`): `Organization` or ID
            filename (str, optional): Absolute path to the local file which should be uploaded
            kwargs (dict, optional): All other optional keyword arguments are applied as key/value
                pairs in the request's JSON payload

        Returns:
        [`Image`](/docs/image)

        Raises:
        [`AirUnexpectedResposne`](/docs/exceptions) - API did not return a 200 OK
            or valid response JSON

        Example:
        ```
        >>> image = air.images.create(name='my_image', filename='/tmp/my_image.qcow2', agent_enabled=False)
        >>> image
        <Image my_image 01298e0c-4ef1-43ec-9675-93160eb29d9f>
        >>> image.upload_status
        'COMPLETE'
        >>> alt_img = air.images.create(name='my_alt_img', filename='/tmp/alt_img.qcow2', agent_enabled=False)
        >>> alt_img.upload_status
        'FAILED'
        ```
        """
        res = self.client.post(self.url, json=kwargs)
        util.raise_if_invalid_response(res, status_code=201)
        image = Image(self, **res.json())
        filename = kwargs.get('filename')
        if filename:
            try:
                image.upload(filename)
            except util.AirUnexpectedResponse as err:
                logger.error(err.message)
            image.refresh()
        return image
