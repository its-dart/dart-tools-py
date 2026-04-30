from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.event_kinds_enum import EventKindsEnum

T = TypeVar("T", bound="Webhook")


@_attrs_define
class Webhook:
    """
    Attributes:
        id (str): The universal, unique ID of the webhook.
        enabled (bool):
        title (str): The webhook title.
        url (str): The URL that webhook events will be sent to.
        event_kinds (list[EventKindsEnum]): The event kinds that will trigger the webhook.
    """

    id: str
    enabled: bool
    title: str
    url: str
    event_kinds: list[EventKindsEnum]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        enabled = self.enabled

        title = self.title

        url = self.url

        event_kinds = []
        for event_kinds_item_data in self.event_kinds:
            event_kinds_item = event_kinds_item_data.value
            event_kinds.append(event_kinds_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "enabled": enabled,
                "title": title,
                "url": url,
                "eventKinds": event_kinds,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        enabled = d.pop("enabled")

        title = d.pop("title")

        url = d.pop("url")

        event_kinds = []
        _event_kinds = d.pop("eventKinds")
        for event_kinds_item_data in _event_kinds:
            event_kinds_item = EventKindsEnum(event_kinds_item_data)

            event_kinds.append(event_kinds_item)

        webhook = cls(
            id=id,
            enabled=enabled,
            title=title,
            url=url,
            event_kinds=event_kinds,
        )

        webhook.additional_properties = d
        return webhook

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
