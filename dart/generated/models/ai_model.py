from enum import Enum


class AiModel(str, Enum):
    AUTO = "auto"
    CLAUDE_FABLE_5 = "claude-fable-5"
    CLAUDE_FABLE_5_1 = "claude-fable-5-1"
    CLAUDE_HAIKU_4_5 = "claude-haiku-4-5"
    CLAUDE_OPUS_5 = "claude-opus-5"
    COMMAND_A_03_2025 = "command-a-03-2025"
    COMMAND_A_PLUS_05_2026 = "command-a-plus-05-2026"
    GEMINI_3_1_FLASH_LITE = "gemini-3.1-flash-lite"
    GEMINI_3_1_PRO_PREVIEW = "gemini-3.1-pro-preview"
    GEMINI_3_7_FLASH = "gemini-3.7-flash"
    GEMINI_3_8_FLASH = "gemini-3.8-flash"
    GLOBAL_AMAZON_NOVA_2_LITE_V10 = "global.amazon.nova-2-lite-v1:0"
    GPT_5_6_LUNA = "gpt-5.6-luna"
    GPT_5_6_SOL = "gpt-5.6-sol"
    GPT_5_6_TERRA = "gpt-5.6-terra"
    GPT_6_ASTRA = "gpt-6-astra"
    GROK_4_20 = "grok-4.20"
    GROK_4_20_MULTI_AGENT = "grok-4.20-multi-agent"
    GROK_4_6 = "grok-4.6"
    MUSE_SPARK_1_1 = "muse-spark-1.1"
    MUSE_SPARK_1_2 = "muse-spark-1.2"
    MUSE_SPARK_1_3 = "muse-spark-1.3"
    US_AMAZON_NOVA_PRO_V10 = "us.amazon.nova-pro-v1:0"

    def __str__(self) -> str:
        return str(self.value)
