from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.text_update_kind import TextUpdateKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="TextUpdate")


@_attrs_define
class TextUpdate:
    """
    Attributes:
        type_ (TextUpdateKind): * `replace` - REPLACE
            * `insert_before` - INSERT_BEFORE
            * `insert_after` - INSERT_AFTER
            * `delete` - DELETE
        old_text (Union[Unset, str]): The exact text to find. Required for "replace" and "delete".
        anchor_text (Union[Unset, str]): The exact text to find as an insertion anchor. Required for "insert_before" and
            "insert_after".
        new_text (Union[Unset, str]): The text to insert. Required for "replace", "insert_before", and "insert_after".
        occurrence (Union[Unset, int]): Which occurrence of oldText or anchorText to act on, 1-indexed. When omitted,
            the search text must be unique in the current content.
    """

    type_: TextUpdateKind
    old_text: Union[Unset, str] = UNSET
    anchor_text: Union[Unset, str] = UNSET
    new_text: Union[Unset, str] = UNSET
    occurrence: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        old_text = self.old_text

        anchor_text = self.anchor_text

        new_text = self.new_text

        occurrence = self.occurrence

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if old_text is not UNSET:
            field_dict["oldText"] = old_text
        if anchor_text is not UNSET:
            field_dict["anchorText"] = anchor_text
        if new_text is not UNSET:
            field_dict["newText"] = new_text
        if occurrence is not UNSET:
            field_dict["occurrence"] = occurrence

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = TextUpdateKind(d.pop("type"))

        old_text = d.pop("oldText", UNSET)

        anchor_text = d.pop("anchorText", UNSET)

        new_text = d.pop("newText", UNSET)

        occurrence = d.pop("occurrence", UNSET)

        text_update = cls(
            type_=type_,
            old_text=old_text,
            anchor_text=anchor_text,
            new_text=new_text,
            occurrence=occurrence,
        )

        text_update.additional_properties = d
        return text_update

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
