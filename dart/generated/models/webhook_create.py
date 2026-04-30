from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.event_kinds_enum import EventKindsEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="WebhookCreate")


@_attrs_define
class WebhookCreate:
    """
    Attributes:
        url (str): The URL that webhook events will be sent to.
        event_kinds (list[EventKindsEnum]): The event kinds that will trigger the webhook.
        enabled (Union[Unset, bool]):
        title (Union[Unset, str]): The webhook title.
    """

    url: str
    event_kinds: list[EventKindsEnum]
    enabled: Union[Unset, bool] = UNSET
    title: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        event_kinds = []
        for event_kinds_item_data in self.event_kinds:
            event_kinds_item = event_kinds_item_data.value
            event_kinds.append(event_kinds_item)

        enabled = self.enabled

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "eventKinds": event_kinds,
            }
        )
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        event_kinds = []
        _event_kinds = d.pop("eventKinds")
        for event_kinds_item_data in _event_kinds:
            event_kinds_item = EventKindsEnum(event_kinds_item_data)

            event_kinds.append(event_kinds_item)

        enabled = d.pop("enabled", UNSET)

        title = d.pop("title", UNSET)

        webhook_create = cls(
            url=url,
            event_kinds=event_kinds,
            enabled=enabled,
            title=title,
        )

        webhook_create.additional_properties = d
        return webhook_create

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
