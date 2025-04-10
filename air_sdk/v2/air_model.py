# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import Field, InitVar, asdict, dataclass, fields, is_dataclass
from datetime import datetime
from functools import cached_property
from typing import (
    Any,
    ClassVar,
    Dict,
    Generic,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    get_origin,
    get_type_hints,
)
from uuid import UUID

from air_sdk.v2 import AirApi
from air_sdk.v2.exceptions import AirError, AirModelAttributeError
from air_sdk.v2.typing import get_list_arg, get_optional_arg, is_optional_union, is_union, type_check
from air_sdk.v2.utils import as_field, is_dunder, iso_string_to_datetime, join_urls, to_uuid

T = TypeVar('T')
TAirModel = TypeVar('TAirModel', bound='AirModel')
TAirModel_co = TypeVar('TAirModel_co', bound='AirModel', covariant=True)
TSupportedPrimitive = TypeVar('TSupportedPrimitive', int, str, float, bool)

PrimaryKey = Union[str, UUID]
SpecialField = Mapping[str, object]
DataDict = Dict[str, Any]


def _generate_special_field() -> SpecialField:
    """Returns a unique mapping reserved for assignment of `metadata` for special `BaseModel` fields."""
    return {'property': object()}


@dataclass(eq=False)
class BaseModel:
    __serializing__ = False  # A flag indicating if the instance is serializing

    def __eq__(self, other: Any) -> bool:
        if type(other) is type(self) and (pk := getattr(self, '__pk__', None)):
            return bool(pk == getattr(other, '__pk__', None))
        return bool(self is other)

    def dict(self) -> DataDict:
        try:
            self.__serializing__ = True
            result = asdict(self)
        finally:
            self.__serializing__ = False
        return result

    def json(self) -> str:
        from air_sdk.v2.endpoints.mixins import serialize_payload

        return serialize_payload(self.dict())


@dataclass(eq=False)
class AirModel(BaseModel, ABC):
    _api: InitVar  # type: ignore[type-arg]
    FIELD_FOREIGN_KEY: ClassVar[SpecialField] = _generate_special_field()
    FIELD_LAZY: ClassVar[SpecialField] = _generate_special_field()

    def __post_init__(self, _api: AirApi) -> None:
        self.__api__ = _api
        self.detail_url = join_urls(self.get_model_api()(self.__api__).url, str(self.__pk__))

    @property
    def primary_key_field(self) -> str:
        """Returns the name of the field representing the primary key."""
        return 'id'

    @property
    def __pk__(self) -> PrimaryKey:
        """
        Returns current model's primary key for API-related actions.
        """
        pk: PrimaryKey = getattr(self, self.primary_key_field)
        return pk

    def __getattribute__(self, name: str) -> Any:
        value = super().__getattribute__(name)

        # filter out dunder attributes (avoids recursion on upcoming `as_field` call)
        if value and not is_dunder(name):
            field = as_field(self, name)

            if field is not None:
                if self.__serializing__ and field.metadata == AirModel.FIELD_FOREIGN_KEY:
                    # When serializing ForeignKey fields use the pk instead of recursively serializing.
                    if isinstance(value, list):
                        return [str(fk.__pk__) for fk in value]
                    return str(value.__pk__)
                if field.metadata == AirModel.FIELD_LAZY and value == AirModel.FIELD_LAZY:
                    value = getattr(  # Resolve Foreign Key fields when their attributes are accessed.
                        self.get_model_api()(self.__api__).get(self.__pk__), name
                    )
                    setattr(self, name, value)
        return value

    def __refresh__(self, refreshed_obj: Optional[BaseModel] = None) -> None:
        """Refreshed the instances data from the backend.

        Raises
        ------
        NotImplementedError - When the model's API does not implement `get`.
        """
        if refreshed_obj is None:
            endpoint_api = self.get_model_api()(self.__api__)
            if endpoint_api is None:
                raise NotImplementedError
            refreshed_obj = endpoint_api.get(pk=self.__pk__)
        for field in fields(self):
            setattr(self, field.name, getattr(refreshed_obj, field.name))

    @classmethod
    @abstractmethod
    def get_model_api(
        cls: Type[TAirModel_co],
    ) -> Type[BaseEndpointApi[TAirModel_co]]:
        """
        Returns the respective `AirModelAPI` type for this model.
        """

    def refresh(self) -> None:
        """Refresh the instance by querying new API data.

        This uses the `get` method on the model's EndpointApi by default.
        """
        self.__refresh__()

    def _ensure_pk_exists(self, context: str) -> None:
        # We cannot perform detailed API calls for instances without populated primary keys
        if self.__pk__ is None:
            raise AirError(f'The {self.__class__.__name__} cannot be {context}: primary key is `None`.')

    def update(self, *args: Any, **kwargs: Any) -> None:
        self._ensure_pk_exists('updated')
        updated_obj = self.get_model_api()(self.__api__).patch(self.__pk__, **kwargs)
        self.__refresh__(updated_obj)  # Ensure update data is reflected in model instance.

    def full_update(self, *args: Any, **kwargs: Any) -> None:
        self._ensure_pk_exists('fully updated')
        updated_obj = self.get_model_api()(self.__api__).put(self.__pk__, **kwargs)
        self.__refresh__(updated_obj)  # Ensure update data is reflected in model instance.

    def delete(self) -> None:
        """Delete the instance and nullify the primary key."""
        self._ensure_pk_exists('deleted')
        self.get_model_api()(self.__api__).delete(self.__pk__)
        setattr(self, self.primary_key_field, None)


class ForeignKeyMixin(Generic[TAirModel_co]):
    """AirModel mixin for lazily resolving the instance."""

    def __init__(self, primary_key: UUID, _api: AirApi) -> None:
        self.__fk__ = primary_key
        self.__fk_resolved__ = False
        self.__api__ = _api

    @property
    def __pk__(self) -> PrimaryKey:
        return self.__fk__

    def __getattribute__(self, name: str) -> Any:
        """Loads the instance upon initial access to an exposed attribute."""
        if not is_dunder(name) and as_field(self, name) is not None and not self.__fk_resolved__:
            self.__refresh__()
            self.__fk_resolved__ = True

        return super().__getattribute__(name)


class ApiNotImplementedMixin:
    """Mixin used to allow AirModel subclasses to have an unimplemented API."""

    def __refresh__(self, refreshed_obj: Optional[BaseModel] = None) -> None:
        if refreshed_obj is None and getattr(self, '__fk_resolved__', True) is True:
            raise NotImplementedError
        super().__refresh__(refreshed_obj)  # type: ignore[misc]


class EndpointMethodMixin:
    """Mixin class for defining common endpoint methods.

    This is used to prevent with the intention of raising
    a `NotImplementedError` instead of an `AttributeError` when
    specific endpoint methods are not implemented in the SDK or API.
    """

    def list(self, **kwargs: Any) -> Iterator[AirModel]:
        raise NotImplementedError

    def create(self, *args: Any, **kwargs: Any) -> AirModel:
        raise NotImplementedError

    def get(self, *args: Any, **kwargs: Any) -> AirModel:
        raise NotImplementedError

    def put(self, *args: Any, **kwargs: Any) -> AirModel:
        raise NotImplementedError

    def patch(self, *args: Any, **kwargs: Any) -> AirModel:
        raise NotImplementedError

    def delete(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError


class BaseEndpointApi(EndpointMethodMixin, Generic[TAirModel_co]):
    model: Type[TAirModel_co]
    API_PATH: str = ''
    url: str

    def __init__(self, api: AirApi):
        self.__api__ = api
        self.url = join_urls(self.__api__.client.base_url, self.API_PATH)

    @cached_property
    def model_cls_type_hints(self) -> DataDict:
        return get_type_hints(self.model)

    @cached_property
    def model_cls_fields(self) -> Tuple[Field[Any], ...]:
        return fields(self.model)

    def load_model(self, data: DataDict) -> TAirModel_co:
        """Construct a new model instance, validate data, and set the API Client."""
        provided_fields = [f for f in self.model_cls_fields if f.name in data]
        missing_fields = [f for f in self.model_cls_fields if f.name not in data]

        try:
            model_inst = self.model(
                _api=self.__api__,
                **self.parse_provided_fields(provided_fields, data),
                **self.get_defaults_for_special_missing_fields(missing_fields),
            )
            return model_inst
        except TypeError as e:
            raise AirModelAttributeError(f'failed to instantiate `{self.model}`: {e}') from None

    def get_defaults_for_special_missing_fields(self, dc_fields: List[Field[Any]]) -> DataDict:
        special_fields: Dict[str, Union[object, None]] = {}
        for field in dc_fields:
            if field.metadata == AirModel.FIELD_LAZY:
                # lazy fields which are not present are assigned a placeholder value
                special_fields[field.name] = AirModel.FIELD_LAZY
            elif is_optional_union(self.model_cls_type_hints[field.name]):
                # optional fields which are not present are assigned to `None`
                special_fields[field.name] = None
        return special_fields

    def parse_provided_fields(self, dc_fields: List[Field[Any]], data: DataDict) -> DataDict:
        return {
            field.name: self.parse_field(
                self.model_cls_type_hints[field.name],
                field.metadata,
                data[field.name],
                f'field `{field.name}` of `{self.model.__name__}`',
            )
            for field in dc_fields
        }

    def parse_field(
        self,
        hint: Type[T],
        metadata: Mapping[Any, Any],
        provided_value: Any,
        context: str,
    ) -> T:
        """Parse the provided value based on the type hint of the value.

        This allows us to perform type checking of provided values and assists in
        the implementation of our `FIELD_FOREIGN_KEY` and `FIELD_LAZY` fields.
        """
        origin = get_origin(hint)
        try:
            if origin is not None:
                if isinstance(origin, type) and issubclass(origin, list):
                    return cast(
                        T, self.handle_list_field(cast(Type[List[T]], hint), metadata, provided_value)
                    )
                elif isinstance(origin, type) and issubclass(origin, dict):
                    return cast(T, provided_value)
                elif is_optional_union(hint):  # field is optional
                    return cast(
                        T, self.handle_optional_field(cast(Type[Optional[T]], hint), metadata, provided_value)
                    )
            elif isinstance(hint, type):  # field is an AirModel
                if issubclass(hint, AirModel):
                    return self.handle_air_model_field(hint, metadata, provided_value)  # type: ignore
                elif is_dataclass(hint) and isinstance(provided_value, dict):
                    return cast(hint, hint(**provided_value))  # type: ignore[valid-type]
                elif issubclass(hint, datetime):  # field is a datetime object
                    return cast(hint, self.handle_datetime_field(provided_value))  # type: ignore
                elif issubclass(hint, (int, str, bool, float)):  # field is a primitive
                    return self.handle_primitive_field(hint, provided_value)  # type: ignore
            if (
                is_union(hint)
                and type_check(provided_value, hint)
                and isinstance(provided_value, (bool, str, int, list, dict, float))
            ):
                return provided_value  # type: ignore
            raise AirModelAttributeError()
        except AirModelAttributeError as e:
            e.args = (f'{context}: {e}',) + e.args[1:]
            raise

    def handle_list_field(
        self, hint: Type[List[T]], metadata: Mapping[Any, Any], provided_value: Union[Any, List[Any]]
    ) -> List[T]:
        """
        Provided `data` argument is validated to be an actual list.
        Each item in `data` list is then validated against the target type and parsed individually.
        """
        if not isinstance(provided_value, list):
            raise AirModelAttributeError(
                f'field data is of type `{type(provided_value).__name__}`, expected `{list}`: {provided_value}'
            )

        return [
            self.parse_field(get_list_arg(hint), metadata, data_item, f'item at index `{index}`')
            for index, data_item in enumerate(provided_value)
        ]

    def handle_optional_field(
        self,
        hint: Type[Optional[T]],
        metadata: Mapping[Any, Any],
        provided_value: Any,
    ) -> Optional[T]:
        if provided_value is None:
            return None
        return self.parse_field(get_optional_arg(hint), metadata, provided_value, 'optional field')

    def handle_air_model_field(
        self,
        hint: Type[TAirModel_co],
        metadata: Mapping[Any, Any],
        provided_value: Any,
    ) -> TAirModel_co:
        """
        `AirModel` fields are validated as follows:
        - Foreign key fields are reserved for on-demand loading
        - Otherwise, field is parsed as a regular `BaseModel`
        """
        if metadata == hint.FIELD_FOREIGN_KEY:
            if isinstance(provided_value, str) or isinstance(provided_value, UUID):
                if primary_key := to_uuid(str(provided_value)):
                    lazy_fk = cast(
                        hint,  # type: ignore
                        type(str(hint.__name__), (ForeignKeyMixin, hint), {})(primary_key, _api=self.__api__),
                    )
                    return lazy_fk
                raise AirModelAttributeError(
                    f'`{hint.__name__}` can not be parsed from foreign key due to invalid UUID value: {provided_value}'
                )
            elif isinstance(provided_value, hint):
                return provided_value

        if isinstance(provided_value, dict):
            fk_api = hint.get_model_api()(self.__api__)
            return fk_api.load_model(provided_value)

        raise AirModelAttributeError(
            f'`{hint.__name__}` can not be parsed from foreign key due to invalid value: {provided_value}'
        )

    def handle_datetime_field(self, provided_value: Any) -> datetime:
        if isinstance(provided_value, datetime):
            return provided_value

        elif isinstance(provided_value, str):
            value = iso_string_to_datetime(provided_value)
            if value is None:
                raise AirModelAttributeError(f'field data is not a valid ISO string: {provided_value}')

            return value

        raise AirModelAttributeError(
            f'`{datetime}` field can not be parsed from field data of type `{type(provided_value).__name__}`: {provided_value}'
        )

    def handle_primitive_field(
        self,
        hint: Type[TSupportedPrimitive],
        provided_value: Any,
    ) -> TSupportedPrimitive:
        """Primitive fields are validated for type mismatch and returned as-is."""
        if not isinstance(provided_value, hint):
            raise AirModelAttributeError(
                f'field data is of type `{type(provided_value).__name__}`, expected `{hint.__name__}`: {provided_value}'
            )
        return provided_value
