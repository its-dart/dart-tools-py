from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ai_model import AiModel
from ..models.ai_thinking_level import AiThinkingLevel
from ..types import UNSET, Unset

T = TypeVar("T", bound="AgentInstructions")


@_attrs_define
class AgentInstructions:
    """
    Attributes:
        markdown (str | Unset): The agent's instructions in markdown format.
        model (AiModel | Unset): * `auto` - AUTO
            * `gpt-6-astra` - GPT_6_ASTRA
            * `gpt-6.1-sol` - GPT_6_1_SOL
            * `gpt-6-luna` - GPT_6_LUNA
            * `claude-fable-5-1` - CLAUDE_FABLE_5_1
            * `claude-opus-5-5` - CLAUDE_OPUS_5_5
            * `claude-sonnet-5-5` - CLAUDE_SONNET_5_5
            * `gemini-3.1-flash-lite` - GEMINI_3_1_FLASH_LITE
            * `gemini-3.8-flash` - GEMINI_3_8_FLASH
            * `gemini-4-argon` - GEMINI_4_ARGON
            * `grok-4.7` - GROK_4_7
            * `grok-4.20` - GROK_4_20
            * `muse-wonder-1.0` - MUSE_WONDER_1_0
            * `muse-spark-1.3` - MUSE_SPARK_1_3
            * `global.amazon.nova-2-lite-v1:0` - NOVA_2_LITE
            * `us.amazon.nova-pro-v1:0` - NOVA_PRO_1_0
            * `command-a-plus-05-2026` - COMMAND_A_PLUS
            * `command-a-03-2025` - COMMAND_A
        thinking_level (AiThinkingLevel | Unset): * `none` - NONE
            * `low` - LOW
            * `medium` - MEDIUM
            * `high` - HIGH
            * `xhigh` - XHIGH
        web_enabled (bool | Unset): Whether web access is enabled for instructions agents.
    """

    markdown: str | Unset = UNSET
    model: AiModel | Unset = UNSET
    thinking_level: AiThinkingLevel | Unset = UNSET
    web_enabled: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        markdown = self.markdown

        model: str | Unset = UNSET
        if not isinstance(self.model, Unset):
            model = self.model.value

        thinking_level: str | Unset = UNSET
        if not isinstance(self.thinking_level, Unset):
            thinking_level = self.thinking_level.value

        web_enabled = self.web_enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if markdown is not UNSET:
            field_dict["markdown"] = markdown
        if model is not UNSET:
            field_dict["model"] = model
        if thinking_level is not UNSET:
            field_dict["thinkingLevel"] = thinking_level
        if web_enabled is not UNSET:
            field_dict["webEnabled"] = web_enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        markdown = d.pop("markdown", UNSET)

        _model = d.pop("model", UNSET)
        model: AiModel | Unset
        if isinstance(_model, Unset):
            model = UNSET
        else:
            model = AiModel(_model)

        _thinking_level = d.pop("thinkingLevel", UNSET)
        thinking_level: AiThinkingLevel | Unset
        if isinstance(_thinking_level, Unset):
            thinking_level = UNSET
        else:
            thinking_level = AiThinkingLevel(_thinking_level)

        web_enabled = d.pop("webEnabled", UNSET)

        agent_instructions = cls(
            markdown=markdown,
            model=model,
            thinking_level=thinking_level,
            web_enabled=web_enabled,
        )

        agent_instructions.additional_properties = d
        return agent_instructions

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
