from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.agent_execution_mode import AgentExecutionMode

if TYPE_CHECKING:
    from ..models.agent_forwarding import AgentForwarding
    from ..models.agent_instructions import AgentInstructions
    from ..models.agent_local import AgentLocal


T = TypeVar("T", bound="Agent")


@_attrs_define
class Agent:
    """
    Attributes:
        id (str): The universal, unique ID of the agent.
        name (str): The display name of the agent.
        enabled (bool): Whether the agent is currently enabled.
        execution_mode (AgentExecutionMode): * `Instructions` - INSTRUCTIONS
            * `Forwarding` - FORWARDING
            * `Local` - LOCAL
            * `None` - NONE
        instructions (AgentInstructions):
        forwarding (AgentForwarding):
        local (AgentLocal):
    """

    id: str
    name: str
    enabled: bool
    execution_mode: AgentExecutionMode
    instructions: "AgentInstructions"
    forwarding: "AgentForwarding"
    local: "AgentLocal"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        enabled = self.enabled

        execution_mode = self.execution_mode.value

        instructions = self.instructions.to_dict()

        forwarding = self.forwarding.to_dict()

        local = self.local.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "enabled": enabled,
                "executionMode": execution_mode,
                "instructions": instructions,
                "forwarding": forwarding,
                "local": local,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_forwarding import AgentForwarding
        from ..models.agent_instructions import AgentInstructions
        from ..models.agent_local import AgentLocal

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        enabled = d.pop("enabled")

        execution_mode = AgentExecutionMode(d.pop("executionMode"))

        instructions = AgentInstructions.from_dict(d.pop("instructions"))

        forwarding = AgentForwarding.from_dict(d.pop("forwarding"))

        local = AgentLocal.from_dict(d.pop("local"))

        agent = cls(
            id=id,
            name=name,
            enabled=enabled,
            execution_mode=execution_mode,
            instructions=instructions,
            forwarding=forwarding,
            local=local,
        )

        agent.additional_properties = d
        return agent

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
