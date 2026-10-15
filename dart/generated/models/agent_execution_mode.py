from enum import StrEnum


class AgentExecutionMode(StrEnum):
    FORWARDING = "Forwarding"
    INSTRUCTIONS = "Instructions"
    LOCAL = "Local"
    NONE = "None"

    def __str__(self) -> str:
        return str(self.value)
