from enum import Enum


class LocalAgent(str, Enum):
    CLAUDE = "claude"
    CODEX = "codex"
    COPILOT = "copilot"
    CURSOR = "cursor"
    GEMINI = "gemini"
    OPENCODE = "opencode"

    def __str__(self) -> str:
        return str(self.value)
