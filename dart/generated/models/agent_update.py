from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.agent_execution_mode import AgentExecutionMode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_forwarding import AgentForwarding
    from ..models.agent_instructions import AgentInstructions
    from ..models.agent_local import AgentLocal


T = TypeVar("T", bound="AgentUpdate")


@_attrs_define
class AgentUpdate:
    """
    Attributes:
        id (str): The universal, unique ID of the agent.
        name (Union[Unset, str]): The new display name for the agent.
        execution_mode (Union[Unset, AgentExecutionMode]): * `Instructions` - INSTRUCTIONS
            * `Forwarding` - FORWARDING
            * `Local` - LOCAL
            * `None` - NONE
        instructions (Union[Unset, AgentInstructions]):
        forwarding (Union[Unset, AgentForwarding]):
        local (Union[Unset, AgentLocal]):
    """

    id: str
    name: Union[Unset, str] = UNSET
    execution_mode: Union[Unset, AgentExecutionMode] = UNSET
    instructions: Union[Unset, "AgentInstructions"] = UNSET
    forwarding: Union[Unset, "AgentForwarding"] = UNSET
    local: Union[Unset, "AgentLocal"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        execution_mode: Union[Unset, str] = UNSET
        if not isinstance(self.execution_mode, Unset):
            execution_mode = self.execution_mode.value

        instructions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.instructions, Unset):
            instructions = self.instructions.to_dict()

        forwarding: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.forwarding, Unset):
            forwarding = self.forwarding.to_dict()

        local: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.local, Unset):
            local = self.local.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if execution_mode is not UNSET:
            field_dict["executionMode"] = execution_mode
        if instructions is not UNSET:
            field_dict["instructions"] = instructions
        if forwarding is not UNSET:
            field_dict["forwarding"] = forwarding
        if local is not UNSET:
            field_dict["local"] = local

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_forwarding import AgentForwarding
        from ..models.agent_instructions import AgentInstructions
        from ..models.agent_local import AgentLocal

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name", UNSET)

        _execution_mode = d.pop("executionMode", UNSET)
        execution_mode: Union[Unset, AgentExecutionMode]
        if isinstance(_execution_mode, Unset):
            execution_mode = UNSET
        else:
            execution_mode = AgentExecutionMode(_execution_mode)

        _instructions = d.pop("instructions", UNSET)
        instructions: Union[Unset, AgentInstructions]
        if isinstance(_instructions, Unset):
            instructions = UNSET
        else:
            instructions = AgentInstructions.from_dict(_instructions)

        _forwarding = d.pop("forwarding", UNSET)
        forwarding: Union[Unset, AgentForwarding]
        if isinstance(_forwarding, Unset):
            forwarding = UNSET
        else:
            forwarding = AgentForwarding.from_dict(_forwarding)

        _local = d.pop("local", UNSET)
        local: Union[Unset, AgentLocal]
        if isinstance(_local, Unset):
            local = UNSET
        else:
            local = AgentLocal.from_dict(_local)

        agent_update = cls(
            id=id,
            name=name,
            execution_mode=execution_mode,
            instructions=instructions,
            forwarding=forwarding,
            local=local,
        )

        agent_update.additional_properties = d
        return agent_update

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
