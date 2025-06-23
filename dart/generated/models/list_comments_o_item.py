from enum import Enum


class ListCommentsOItem(str, Enum):
    HIERARCHICAL = "hierarchical"
    PUBLISHED_AT = "published_at"
    PUBLISHED_AT_DESC = "-published_at"

    def __str__(self) -> str:
        return str(self.value)
