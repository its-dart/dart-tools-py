from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

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
        markdown (Union[Unset, str]): The agent's instructions in markdown format.
        model (Union[Unset, AiModel]): * `auto` - AUTO
            * `gpt-4.1` - GPT_4_1
            * `gpt-5.1` - GPT_5_1
            * `gpt-5.2` - GPT_5_2
            * `gpt-5.4` - GPT_5_4
            * `gpt-5.5` - GPT_5_5
            * `claude-haiku-4-5` - CLAUDE_HAIKU_4_5
            * `claude-sonnet-4-6` - CLAUDE_SONNET_4_6
            * `claude-opus-4-6` - CLAUDE_OPUS_4_6
            * `claude-opus-4-7` - CLAUDE_OPUS_4_7
            * `gemini-3.1-flash-lite-preview` - GEMINI_3_1_FLASH_LITE_PREVIEW
            * `gemini-3.1-pro-preview` - GEMINI_3_1_PRO_PREVIEW
        thinking_level (Union[Unset, AiThinkingLevel]): * `none` - NONE
            * `low` - LOW
            * `medium` - MEDIUM
            * `high` - HIGH
            * `xhigh` - XHIGH
        web_enabled (Union[Unset, bool]): Whether web access is enabled for instructions agents.
    """

    markdown: Union[Unset, str] = UNSET
    model: Union[Unset, AiModel] = UNSET
    thinking_level: Union[Unset, AiThinkingLevel] = UNSET
    web_enabled: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        markdown = self.markdown

        model: Union[Unset, str] = UNSET
        if not isinstance(self.model, Unset):
            model = self.model.value

        thinking_level: Union[Unset, str] = UNSET
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
        model: Union[Unset, AiModel]
        if isinstance(_model, Unset):
            model = UNSET
        else:
            model = AiModel(_model)

        _thinking_level = d.pop("thinkingLevel", UNSET)
        thinking_level: Union[Unset, AiThinkingLevel]
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
