from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UserSpaceConfigurationCustomPropertyDatesTypeDef")


@_attrs_define
class UserSpaceConfigurationCustomPropertyDatesTypeDef:
    """
    Attributes:
        name (str):
        type_ (Literal['Dates']):
        is_range (bool):
    """

    name: str
    type_: Literal["Dates"]
    is_range: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        type_ = self.type_

        is_range = self.is_range

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type": type_,
                "isRange": is_range,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        type_ = cast(Literal["Dates"], d.pop("type"))
        if type_ != "Dates":
            raise ValueError(f"type must match const 'Dates', got '{type_}'")

        is_range = d.pop("isRange")

        user_space_configuration_custom_property_dates_type_def = cls(
            name=name,
            type_=type_,
            is_range=is_range,
        )

        user_space_configuration_custom_property_dates_type_def.additional_properties = d
        return user_space_configuration_custom_property_dates_type_def

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
