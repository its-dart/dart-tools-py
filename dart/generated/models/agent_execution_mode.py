from enum import Enum


class AgentExecutionMode(str, Enum):
    FORWARDING = "Forwarding"
    INSTRUCTIONS = "Instructions"
    LOCAL = "Local"
    NONE = "None"

    def __str__(self) -> str:
        return str(self.value)
