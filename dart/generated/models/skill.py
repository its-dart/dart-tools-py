from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.attachment import Attachment


T = TypeVar("T", bound="Skill")


@_attrs_define
class Skill:
    """
    Attributes:
        id (str): The universal, unique ID of the skill.
        title (str): The title of the skill, describing the task type.
        prompt_markdown (str): User-defined instructions for performing this skill in markdown format.
        attachments (list['Attachment']): Attachments linked to the skill, including their accessible URLs.
    """

    id: str
    title: str
    prompt_markdown: str
    attachments: list["Attachment"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        prompt_markdown = self.prompt_markdown

        attachments = []
        for attachments_item_data in self.attachments:
            attachments_item = attachments_item_data.to_dict()
            attachments.append(attachments_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "title": title,
                "promptMarkdown": prompt_markdown,
                "attachments": attachments,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.attachment import Attachment

        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title")

        prompt_markdown = d.pop("promptMarkdown")

        attachments = []
        _attachments = d.pop("attachments")
        for attachments_item_data in _attachments:
            attachments_item = Attachment.from_dict(attachments_item_data)

            attachments.append(attachments_item)

        skill = cls(
            id=id,
            title=title,
            prompt_markdown=prompt_markdown,
            attachments=attachments,
        )

        skill.additional_properties = d
        return skill

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
