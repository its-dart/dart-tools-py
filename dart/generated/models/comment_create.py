from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CommentCreate")


@_attrs_define
class CommentCreate:
    """
    Attributes:
        task_id (str): The universal, unique ID of the task that the comment is associated with.
        text (str): The full content of the comment, which can include markdown formatting.
        parent_id (Union[Unset, str]): The universal, unique ID of the parent comment, if any.
    """

    task_id: str
    text: str
    parent_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        task_id = self.task_id

        text = self.text

        parent_id = self.parent_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "taskId": task_id,
                "text": text,
            }
        )
        if parent_id is not UNSET:
            field_dict["parentId"] = parent_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        task_id = d.pop("taskId")

        text = d.pop("text")

        parent_id = d.pop("parentId", UNSET)

        comment_create = cls(
            task_id=task_id,
            text=text,
            parent_id=parent_id,
        )

        comment_create.additional_properties = d
        return comment_create

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
