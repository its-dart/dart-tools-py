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

T = TypeVar("T", bound="WebhookUpdate")


@_attrs_define
class WebhookUpdate:
    """
    Attributes:
        id (str): The universal, unique ID of the webhook.
        enabled (Union[Unset, bool]):
        title (Union[Unset, str]): The webhook title.
        url (Union[Unset, str]): The URL that webhook events will be sent to.
        event_kinds (Union[Unset, list[EventKindsEnum]]): The event kinds that will trigger the webhook.
    """

    id: str
    enabled: Union[Unset, bool] = UNSET
    title: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    event_kinds: Union[Unset, list[EventKindsEnum]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        enabled = self.enabled

        title = self.title

        url = self.url

        event_kinds: Union[Unset, list[str]] = UNSET
        if not isinstance(self.event_kinds, Unset):
            event_kinds = []
            for event_kinds_item_data in self.event_kinds:
                event_kinds_item = event_kinds_item_data.value
                event_kinds.append(event_kinds_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if title is not UNSET:
            field_dict["title"] = title
        if url is not UNSET:
            field_dict["url"] = url
        if event_kinds is not UNSET:
            field_dict["eventKinds"] = event_kinds

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        enabled = d.pop("enabled", UNSET)

        title = d.pop("title", UNSET)

        url = d.pop("url", UNSET)

        event_kinds = []
        _event_kinds = d.pop("eventKinds", UNSET)
        for event_kinds_item_data in _event_kinds or []:
            event_kinds_item = EventKindsEnum(event_kinds_item_data)

            event_kinds.append(event_kinds_item)

        webhook_update = cls(
            id=id,
            enabled=enabled,
            title=title,
            url=url,
            event_kinds=event_kinds,
        )

        webhook_update.additional_properties = d
        return webhook_update

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
