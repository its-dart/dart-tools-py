from enum import Enum


class ListTasksOItem(str, Enum):
    CREATED_AT = "created_at"
    DARTBOARD_ORDER = "dartboard__order"
    ORDER = "order"
    TITLE = "title"
    UPDATED_AT = "updated_at"
    VALUE_0 = "-created_at"
    VALUE_1 = "-dartboard__order"
    VALUE_2 = "-order"
    VALUE_3 = "-title"
    VALUE_4 = "-updated_at"

    def __str__(self) -> str:
        return str(self.value)
