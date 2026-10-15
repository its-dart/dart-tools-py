from enum import StrEnum


class UserSpaceConfigurationCustomPropertyNumberTypeDefCustomPropertyNumberFormatTypeDef(StrEnum):
    DOLLARS = "Dollars"
    INTEGER = "Integer"
    PERCENTAGE = "Percentage"

    def __str__(self) -> str:
        return str(self.value)
