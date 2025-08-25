from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="View")


@_attrs_define
class View:
    """
    Attributes:
        id (str): The universal, unique ID of the view.
        html_url (str): The URL that can be used to open the view in the Dart web UI.
        title (str): The title, which is a short description of the view.
        description (str): The description, which is a longer description of the view.
    """

    id: str
    html_url: str
    title: str
    description: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        html_url = self.html_url

        title = self.title

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "htmlUrl": html_url,
                "title": title,
                "description": description,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        html_url = d.pop("htmlUrl")

        title = d.pop("title")

        description = d.pop("description")

        view = cls(
            id=id,
            html_url=html_url,
            title=title,
            description=description,
        )

        view.additional_properties = d
        return view

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
