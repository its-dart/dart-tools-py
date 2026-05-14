from enum import Enum


class AiModel(str, Enum):
    AUTO = "auto"
    CLAUDE_HAIKU_4_5 = "claude-haiku-4-5"
    CLAUDE_OPUS_4_6 = "claude-opus-4-6"
    CLAUDE_OPUS_4_7 = "claude-opus-4-7"
    CLAUDE_SONNET_4_6 = "claude-sonnet-4-6"
    GEMINI_3_1_FLASH_LITE_PREVIEW = "gemini-3.1-flash-lite-preview"
    GEMINI_3_1_PRO_PREVIEW = "gemini-3.1-pro-preview"
    GPT_4_1 = "gpt-4.1"
    GPT_5_1 = "gpt-5.1"
    GPT_5_2 = "gpt-5.2"
    GPT_5_4 = "gpt-5.4"
    GPT_5_5 = "gpt-5.5"

    def __str__(self) -> str:
        return str(self.value)
