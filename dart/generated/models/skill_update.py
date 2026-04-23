from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SkillUpdate")


@_attrs_define
class SkillUpdate:
    """
    Attributes:
        id (str): The universal, unique ID of the skill.
        title (Union[Unset, str]): The title of the skill, describing the task type.
        prompt_markdown (Union[Unset, str]): User-defined instructions for performing this skill in markdown format.
    """

    id: str
    title: Union[Unset, str] = UNSET
    prompt_markdown: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        prompt_markdown = self.prompt_markdown

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if prompt_markdown is not UNSET:
            field_dict["promptMarkdown"] = prompt_markdown

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title", UNSET)

        prompt_markdown = d.pop("promptMarkdown", UNSET)

        skill_update = cls(
            id=id,
            title=title,
            prompt_markdown=prompt_markdown,
        )

        skill_update.additional_properties = d
        return skill_update

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
