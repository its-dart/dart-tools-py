from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TaskRelationships")


@_attrs_define
class TaskRelationships:
    """
    Example:
        {'subtaskIds': ['abcdefghijk1', 'abcdefghijk2'], 'blockerIds': ['abcdefghijk3'], 'blockingIds':
            ['abcdefghijk4'], 'duplicateIds': ['abcdefghijk5'], 'relatedIds': ['abcdefghijk6', 'abcdefghijk7']}

    Attributes:
        subtask_ids (Union[Unset, list[str]]): List of task IDs that are subtasks of this task (PARENT_OF relationship,
            forward direction)
        blocker_ids (Union[Unset, list[str]]): List of task IDs that block this task (BLOCKS relationship, backward
            direction)
        blocking_ids (Union[Unset, list[str]]): List of task IDs that this task blocks (BLOCKS relationship, forward
            direction)
        duplicate_ids (Union[Unset, list[str]]): List of task IDs that are duplicates of this task (DUPLICATES
            relationship, both directions)
        related_ids (Union[Unset, list[str]]): List of task IDs that are related to this task (RELATES_TO relationship,
            both directions)
    """

    subtask_ids: Union[Unset, list[str]] = UNSET
    blocker_ids: Union[Unset, list[str]] = UNSET
    blocking_ids: Union[Unset, list[str]] = UNSET
    duplicate_ids: Union[Unset, list[str]] = UNSET
    related_ids: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        subtask_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.subtask_ids, Unset):
            subtask_ids = self.subtask_ids

        blocker_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.blocker_ids, Unset):
            blocker_ids = self.blocker_ids

        blocking_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.blocking_ids, Unset):
            blocking_ids = self.blocking_ids

        duplicate_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.duplicate_ids, Unset):
            duplicate_ids = self.duplicate_ids

        related_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.related_ids, Unset):
            related_ids = self.related_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if subtask_ids is not UNSET:
            field_dict["subtaskIds"] = subtask_ids
        if blocker_ids is not UNSET:
            field_dict["blockerIds"] = blocker_ids
        if blocking_ids is not UNSET:
            field_dict["blockingIds"] = blocking_ids
        if duplicate_ids is not UNSET:
            field_dict["duplicateIds"] = duplicate_ids
        if related_ids is not UNSET:
            field_dict["relatedIds"] = related_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        subtask_ids = cast(list[str], d.pop("subtaskIds", UNSET))

        blocker_ids = cast(list[str], d.pop("blockerIds", UNSET))

        blocking_ids = cast(list[str], d.pop("blockingIds", UNSET))

        duplicate_ids = cast(list[str], d.pop("duplicateIds", UNSET))

        related_ids = cast(list[str], d.pop("relatedIds", UNSET))

        task_relationships = cls(
            subtask_ids=subtask_ids,
            blocker_ids=blocker_ids,
            blocking_ids=blocking_ids,
            duplicate_ids=duplicate_ids,
            related_ids=related_ids,
        )

        task_relationships.additional_properties = d
        return task_relationships

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
