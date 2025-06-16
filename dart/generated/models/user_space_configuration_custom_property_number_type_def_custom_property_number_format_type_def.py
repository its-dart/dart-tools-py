from enum import Enum


class UserSpaceConfigurationCustomPropertyNumberTypeDefCustomPropertyNumberFormatTypeDef(str, Enum):
    DOLLARS = "Dollars"
    INTEGER = "Integer"
    PERCENTAGE = "Percentage"

    def __str__(self) -> str:
        return str(self.value)
