from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DocUpdate")


@_attrs_define
class DocUpdate:
    """
    Attributes:
        id (str): The universal, unique ID of the doc.
        title (Union[Unset, str]): The title, which is a short description of the doc.
        folder (Union[Unset, str]): The full title of the folder, which is a project or list of docs.
        text (Union[Unset, str]): The full content of the doc, which can include markdown formatting.
    """

    id: str
    title: Union[Unset, str] = UNSET
    folder: Union[Unset, str] = UNSET
    text: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        folder = self.folder

        text = self.text

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if folder is not UNSET:
            field_dict["folder"] = folder
        if text is not UNSET:
            field_dict["text"] = text

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title", UNSET)

        folder = d.pop("folder", UNSET)

        text = d.pop("text", UNSET)

        doc_update = cls(
            id=id,
            title=title,
            folder=folder,
            text=text,
        )

        doc_update.additional_properties = d
        return doc_update

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
