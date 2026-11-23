from enum import StrEnum


class AiModel(StrEnum):
    AUTO = "auto"
    CLAUDE_FABLE_5_2 = "claude-fable-5-2"
    CLAUDE_OPUS_5_5 = "claude-opus-5-5"
    CLAUDE_SONNET_5_5 = "claude-sonnet-5-5"
    COMMAND_A = "command-a-03-2025"
    COMMAND_A_PLUS = "command-a-plus-05-2026"
    GEMINI_4_CARBON = "gemini-4-carbon"
    GEMINI_4_HYDROGEN = "gemini-4-hydrogen"
    GEMINI_4_NEON = "gemini-4-neon"
    GPT_6_2_ASTRA = "gpt-6.2-astra"
    GPT_6_2_SOL = "gpt-6.2-sol"
    GPT_6_LUNA = "gpt-6-luna"
    GROK_4_20 = "grok-4.20"
    GROK_4_7 = "grok-4.7"
    MUSE_SPARK_1_3 = "muse-spark-1.3"
    MUSE_WONDER_1_0 = "muse-wonder-1.0"
    NOVA_2_LITE = "global.amazon.nova-2-lite-v1:0"
    NOVA_PRO_1_0 = "us.amazon.nova-pro-v1:0"

    def __str__(self) -> str:
        return str(self.value)
