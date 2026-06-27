from enum import Enum


class LocalAgent(str, Enum):
    CLAUDE = "claude"
    CODEX = "codex"
    GEMINI = "gemini"
    OPENCODE = "opencode"
    CURSOR = "cursor"
    COPILOT = "copilot"

    def __str__(self) -> str:
        return str(self.value)
