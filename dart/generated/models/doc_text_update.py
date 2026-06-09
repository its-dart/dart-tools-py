from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.text_update import TextUpdate


T = TypeVar("T", bound="DocTextUpdate")


@_attrs_define
class DocTextUpdate:
    """Payload for applying a list of targeted text updates to a doc's text content.

    Attributes:
        updates (list['TextUpdate']): An ordered list of text updates to apply. Each one operates on the result of the
            previous one. Applied atomically — if any update fails, none are persisted.
    """

    updates: list["TextUpdate"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        updates = []
        for updates_item_data in self.updates:
            updates_item = updates_item_data.to_dict()
            updates.append(updates_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "updates": updates,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.text_update import TextUpdate

        d = dict(src_dict)
        updates = []
        _updates = d.pop("updates")
        for updates_item_data in _updates:
            updates_item = TextUpdate.from_dict(updates_item_data)

            updates.append(updates_item)

        doc_text_update = cls(
            updates=updates,
        )

        doc_text_update.additional_properties = d
        return doc_text_update

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
