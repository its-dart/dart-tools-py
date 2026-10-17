from enum import StrEnum


class ListCommentsOItem(StrEnum):
    HIERARCHICAL = "hierarchical"
    PUBLISHED_AT = "published_at"
    PUBLISHED_AT_DESC = "-published_at"

    def __str__(self) -> str:
        return str(self.value)
