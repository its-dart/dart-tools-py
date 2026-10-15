from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Doc")


@_attrs_define
class Doc:
    """
    Attributes:
        id (str): The universal, unique ID of the doc.
        html_url (str): The URL that can be used to open the doc in the Dart web UI.
        title (str): The title, which is a short description of the doc.
        folder (str): The full title of the folder, which is a project or list of docs.
        text (str): The full content of the doc, which can include markdown formatting.
    """

    id: str
    html_url: str
    title: str
    folder: str
    text: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        html_url = self.html_url

        title = self.title

        folder = self.folder

        text = self.text

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "htmlUrl": html_url,
                "title": title,
                "folder": folder,
                "text": text,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        html_url = d.pop("htmlUrl")

        title = d.pop("title")

        folder = d.pop("folder")

        text = d.pop("text")

        doc = cls(
            id=id,
            html_url=html_url,
            title=title,
            folder=folder,
            text=text,
        )

        doc.additional_properties = d
        return doc

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
