from enum import Enum


class LocalAgent(str, Enum):
    AGY = "agy"
    CLAUDE = "claude"
    CODEX = "codex"
    COPILOT = "copilot"
    CURSOR = "cursor"
    DEVIN = "devin"
    GEMINI = "gemini"
    GROK = "grok"
    MUSE = "muse"
    OPENCODE = "opencode"
    PRIME_AGENT = "prime-agent"
    VIBE = "vibe"

    def __str__(self) -> str:
        return str(self.value)
