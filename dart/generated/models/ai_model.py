from enum import StrEnum


class AiModel(StrEnum):
    AUTO = "auto"
    CLAUDE_FABLE_5_1 = "claude-fable-5-1"
    CLAUDE_OPUS_5_5 = "claude-opus-5-5"
    CLAUDE_SONNET_5_5 = "claude-sonnet-5-5"
    COMMAND_A = "command-a-03-2025"
    COMMAND_A_PLUS = "command-a-plus-05-2026"
    GEMINI_3_1_FLASH_LITE = "gemini-3.1-flash-lite"
    GEMINI_3_8_FLASH = "gemini-3.8-flash"
    GEMINI_4_ARGON = "gemini-4-argon"
    GPT_6_1_SOL = "gpt-6.1-sol"
    GPT_6_ASTRA = "gpt-6-astra"
    GPT_6_LUNA = "gpt-6-luna"
    GROK_4_20 = "grok-4.20"
    GROK_4_7 = "grok-4.7"
    MUSE_SPARK_1_3 = "muse-spark-1.3"
    MUSE_WONDER_1_0 = "muse-wonder-1.0"
    NOVA_2_LITE = "global.amazon.nova-2-lite-v1:0"
    NOVA_PRO_1_0 = "us.amazon.nova-pro-v1:0"

    def __str__(self) -> str:
        return str(self.value)
