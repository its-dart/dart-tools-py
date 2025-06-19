from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UserSpaceConfigurationCustomPropertyTextTypeDef")


@_attrs_define
class UserSpaceConfigurationCustomPropertyTextTypeDef:
    """
    Attributes:
        name (str):
        type_ (Literal['Text']):
    """

    name: str
    type_: Literal["Text"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        type_ = cast(Literal["Text"], d.pop("type"))
        if type_ != "Text":
            raise ValueError(f"type must match const 'Text', got '{type_}'")

        user_space_configuration_custom_property_text_type_def = cls(
            name=name,
            type_=type_,
        )

        user_space_configuration_custom_property_text_type_def.additional_properties = d
        return user_space_configuration_custom_property_text_type_def

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
