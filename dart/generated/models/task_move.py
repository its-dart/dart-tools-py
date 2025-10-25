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
        before_task_id (Union[None, Unset, str]): Move the task immediately before this task. For example: if tasks are
            [A, B, C], then beforeTaskId=B produces [A, moved_task, B, C]. Use null to move to the beginning (first
            position).
        after_task_id (Union[None, Unset, str]): Move the task immediately after this task. For example: if tasks are
            [A, B, C], then afterTaskId=B produces [A, B, moved_task, C]. Use null to move to the end (last position).
    """

    before_task_id: Union[None, Unset, str] = UNSET
    after_task_id: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        before_task_id: Union[None, Unset, str]
        if isinstance(self.before_task_id, Unset):
            before_task_id = UNSET
        else:
            before_task_id = self.before_task_id

        after_task_id: Union[None, Unset, str]
        if isinstance(self.after_task_id, Unset):
            after_task_id = UNSET
        else:
            after_task_id = self.after_task_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if before_task_id is not UNSET:
            field_dict["beforeTaskId"] = before_task_id
        if after_task_id is not UNSET:
            field_dict["afterTaskId"] = after_task_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_before_task_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        before_task_id = _parse_before_task_id(d.pop("beforeTaskId", UNSET))

        def _parse_after_task_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        after_task_id = _parse_after_task_id(d.pop("afterTaskId", UNSET))

        task_move = cls(
            before_task_id=before_task_id,
            after_task_id=after_task_id,
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
