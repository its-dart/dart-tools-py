from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_forwarding_headers import AgentForwardingHeaders


T = TypeVar("T", bound="AgentForwarding")


@_attrs_define
class AgentForwarding:
    """
    Attributes:
        url (str | Unset): The URL to call when the agent is triggered.
        headers (AgentForwardingHeaders | Unset): Headers to include with the forwarding request.
        body (str | Unset): The JSON body template for the forwarding request.
        response_key (str | Unset): The JSON response key to use as the agent's comment.
    """

    url: str | Unset = UNSET
    headers: AgentForwardingHeaders | Unset = UNSET
    body: str | Unset = UNSET
    response_key: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:

        url: str | Unset
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        headers: dict[str, Any] | Unset = UNSET
        if not isinstance(self.headers, Unset):
            headers = self.headers.to_dict()

        body = self.body

        response_key = self.response_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if headers is not UNSET:
            field_dict["headers"] = headers
        if body is not UNSET:
            field_dict["body"] = body
        if response_key is not UNSET:
            field_dict["responseKey"] = response_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_forwarding_headers import AgentForwardingHeaders  # noqa: PLC0415

        d = dict(src_dict)

        def _parse_url(data: object) -> str | Unset:
            if isinstance(data, Unset):
                return data
            return cast(str | Unset, data)

        url = _parse_url(d.pop("url", UNSET))

        _headers = d.pop("headers", UNSET)
        headers: AgentForwardingHeaders | Unset
        if isinstance(_headers, Unset):
            headers = UNSET
        else:
            headers = AgentForwardingHeaders.from_dict(_headers)

        body = d.pop("body", UNSET)

        response_key = d.pop("responseKey", UNSET)

        agent_forwarding = cls(
            url=url,
            headers=headers,
            body=body,
            response_key=response_key,
        )

        agent_forwarding.additional_properties = d
        return agent_forwarding

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
