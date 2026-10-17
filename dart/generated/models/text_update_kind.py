from enum import StrEnum


class TextUpdateKind(StrEnum):
    DELETE = "delete"
    INSERT_AFTER = "insert_after"
    INSERT_BEFORE = "insert_before"
    REPLACE = "replace"

    def __str__(self) -> str:
        return str(self.value)
