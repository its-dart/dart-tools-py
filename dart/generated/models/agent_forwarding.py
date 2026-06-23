from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

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
        url (Union[Unset, str]): The URL to call when the agent is triggered.
        headers (Union[Unset, AgentForwardingHeaders]): Headers to include with the forwarding request.
        body (Union[Unset, str]): The JSON body template for the forwarding request.
        response_key (Union[Unset, str]): The JSON response key to use as the agent's comment.
    """

    url: Union[Unset, str] = UNSET
    headers: Union[Unset, "AgentForwardingHeaders"] = UNSET
    body: Union[Unset, str] = UNSET
    response_key: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        headers: Union[Unset, dict[str, Any]] = UNSET
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
        from ..models.agent_forwarding_headers import AgentForwardingHeaders

        d = dict(src_dict)
        url = d.pop("url", UNSET)

        _headers = d.pop("headers", UNSET)
        headers: Union[Unset, AgentForwardingHeaders]
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
