from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any, Union

from air_sdk.util import raise_if_invalid_response
from air_sdk.v2.air_model import AirModel, PrimaryKey, BaseEndpointApi
from air_sdk.v2.endpoints.mixins import serialize_payload
from air_sdk.v2.endpoints.nodes import Node
from air_sdk.v2.endpoints.user_configs import UserConfig
from air_sdk.v2.utils import validate_payload_types


@dataclass(eq=False)
class CloudInit(AirModel):
    simulation_node: Node = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    user_data: Optional[UserConfig] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    meta_data: Optional[UserConfig] = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    user_data_name: Optional[str] = field(repr=False)
    meta_data_name: Optional[str] = field(repr=False)

    @classmethod
    def get_model_api(cls):
        """
        Returns the respective `AirModelAPI` type for this model.
        """
        return CloudInitEndpointApi

    @property
    def primary_key_field(self) -> str:
        return 'simulation_node'

    @property
    def __pk__(self) -> PrimaryKey:
        return getattr(self, self.primary_key_field).__pk__  # type: ignore

    @validate_payload_types
    def full_update(
        self,
        user_data: Optional[Union[UserConfig, PrimaryKey]],
        meta_data: Optional[Union[UserConfig, PrimaryKey]],
    ) -> None:
        """Update all fields of the cloud-init assignment."""
        super().update(user_data=user_data, meta_data=meta_data)


class CloudInitEndpointApi(BaseEndpointApi[CloudInit]):
    API_PATH = 'simulations/nodes/{id}/cloud-init'  # Placeholder
    model = CloudInit

    def get(self, pk: PrimaryKey, **params: Any) -> CloudInit:
        detail_url = self.url.format(id=str(pk))
        response = self.__api__.client.get(detail_url, params=params)
        raise_if_invalid_response(response)
        return self.load_model(response.json())

    def patch(self, pk: PrimaryKey, **kwargs: Any) -> CloudInit:
        detail_url = self.url.format(id=str(pk))
        response = self.__api__.client.patch(detail_url, data=serialize_payload(kwargs))
        raise_if_invalid_response(response)
        return self.load_model(response.json())
