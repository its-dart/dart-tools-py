from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TaskMove")


@_attrs_define
class TaskMove:
    """
    Attributes:
        insert_before_id (Union[None, Unset, str]): Move the task to immediately before the provided task ID. Use null
            to move the task to the beginning of the dartboard.
        insert_after_id (Union[None, Unset, str]): Move the task to immediately after the provided task ID. Use null to
            move the task to the end of the dartboard.
    """

    insert_before_id: Union[None, Unset, str] = UNSET
    insert_after_id: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        insert_before_id: Union[None, Unset, str]
        if isinstance(self.insert_before_id, Unset):
            insert_before_id = UNSET
        else:
            insert_before_id = self.insert_before_id

        insert_after_id: Union[None, Unset, str]
        if isinstance(self.insert_after_id, Unset):
            insert_after_id = UNSET
        else:
            insert_after_id = self.insert_after_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if insert_before_id is not UNSET:
            field_dict["insertBeforeId"] = insert_before_id
        if insert_after_id is not UNSET:
            field_dict["insertAfterId"] = insert_after_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_insert_before_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        insert_before_id = _parse_insert_before_id(d.pop("insertBeforeId", UNSET))

        def _parse_insert_after_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        insert_after_id = _parse_insert_after_id(d.pop("insertAfterId", UNSET))

        task_move = cls(
            insert_before_id=insert_before_id,
            insert_after_id=insert_after_id,
        )

        task_move.additional_properties = d
        return task_move

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
