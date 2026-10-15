from enum import StrEnum


class Priority(StrEnum):
    CRITICAL = "Critical"
    HIGH = "High"
    LOW = "Low"
    MEDIUM = "Medium"

    def __str__(self) -> str:
        return str(self.value)
