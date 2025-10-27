from enum import Enum


class ListTasksOItem(str, Enum):
    CREATED_AT = "created_at"
    DARTBOARD_ORDER = "dartboard__order"
    ORDER = "order"
    TITLE = "title"
    UPDATED_AT = "updated_at"
    CREATED_AT_DESC = "-created_at"
    DARTBOARD_ORDER_DESC = "-dartboard__order"
    ORDER_DESC = "-order"
    TITLE_DESC = "-title"
    UPDATED_AT_DESC = "-updated_at"

    def __str__(self) -> str:
        return str(self.value)
