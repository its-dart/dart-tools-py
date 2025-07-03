from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="TaskRelationships")


@_attrs_define
class TaskRelationships:
    """
    Example:
        {'subtaskIds': ['abcdefghijk1', 'abcdefghijk2'], 'blockerIds': ['abcdefghijk3'], 'blockingIds':
            ['abcdefghijk4'], 'duplicateIds': ['abcdefghijk5'], 'relatedIds': ['abcdefghijk6', 'abcdefghijk7']}

    Attributes:
        subtask_ids (Union[Unset, list[str]]): List of task IDs that are subtasks of this task
        blocker_ids (Union[Unset, list[str]]): List of task IDs that block this task
        blocking_ids (Union[Unset, list[str]]): List of task IDs that this task blocks
        duplicate_ids (Union[Unset, list[str]]): List of task IDs that are duplicates of this task
        related_ids (Union[Unset, list[str]]): List of task IDs that are related to this task
    """

    subtask_ids: Union[Unset, list[str]] = UNSET
    blocker_ids: Union[Unset, list[str]] = UNSET
    blocking_ids: Union[Unset, list[str]] = UNSET
    duplicate_ids: Union[Unset, list[str]] = UNSET
    related_ids: Union[Unset, list[str]] = UNSET

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

        return task_relationships
