from enum import Enum


class TextUpdateKind(str, Enum):
    DELETE = "delete"
    INSERT_AFTER = "insert_after"
    INSERT_BEFORE = "insert_before"
    REPLACE = "replace"

    def __str__(self) -> str:
        return str(self.value)
