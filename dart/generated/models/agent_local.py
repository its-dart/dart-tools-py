from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.local_agent import LocalAgent
from ..types import UNSET, Unset

T = TypeVar("T", bound="AgentLocal")


@_attrs_define
class AgentLocal:
    """
    Attributes:
        agent (Union[Unset, LocalAgent]): * `claude` - CLAUDE
            * `codex` - CODEX
            * `gemini` - GEMINI
            * `opencode` - OPENCODE
    """

    agent: Union[Unset, LocalAgent] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent: Union[Unset, str] = UNSET
        if not isinstance(self.agent, Unset):
            agent = self.agent.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if agent is not UNSET:
            field_dict["agent"] = agent

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _agent = d.pop("agent", UNSET)
        agent: Union[Unset, LocalAgent]
        if isinstance(_agent, Unset):
            agent = UNSET
        else:
            agent = LocalAgent(_agent)

        agent_local = cls(
            agent=agent,
        )

        agent_local.additional_properties = d
        return agent_local

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
