from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TaskCreateCustomPropertiesType0")


@_attrs_define
class TaskCreateCustomPropertiesType0:
    """Custom properties as a dict mapping property NAME to value. Use exact property names from workspace config (e.g.,
    {"customCheckboxProperty": true, "customTextProperty": "Some text"}). Property names are case-sensitive.

        Example:
            {'customCheckboxProperty': True, 'customDatesProperty': '2025-05-10', 'customDatesPropertyWithRange':
                ['2025-05-01', '2025-05-30'], 'customMultiselectProperty': ['frontend', 'bug'],
                'customNumberPropertyWithIntegerFormat': 5, 'customNumberPropertyWithPercentageFormat': 75,
                'customNumberPropertyWithDollarsFormat': 1500.5, 'customSelectProperty': 'In Progress', 'customStatusProperty':
                'Blocked', 'customTextProperty': 'This task requires additional review from the design team',
                'customUserProperty': 'john.doe@example.com', 'customMultipleUserProperty': ['john.doe@example.com', 'Alice
                Smith']}

    """

    additional_properties: dict[str, Union[None, bool, float, int, list[Union[None, str]], list[str], str]] = (
        _attrs_field(init=False, factory=dict)
    )

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            if isinstance(prop, list):
                field_dict[prop_name] = []
                for additional_property_custom_property_dates_range_type_0_item_data in prop:
                    additional_property_custom_property_dates_range_type_0_item: Union[None, str]
                    additional_property_custom_property_dates_range_type_0_item = (
                        additional_property_custom_property_dates_range_type_0_item_data
                    )
                    field_dict[prop_name].append(additional_property_custom_property_dates_range_type_0_item)

            elif isinstance(prop, list):
                field_dict[prop_name] = prop

            elif isinstance(prop, list):
                field_dict[prop_name] = prop

            else:
                field_dict[prop_name] = prop

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        task_create_custom_properties_type_0 = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():

            def _parse_additional_property(
                data: object,
            ) -> Union[None, bool, float, int, list[Union[None, str]], list[str], str]:
                if data is None:
                    return data
                try:
                    if not isinstance(data, list):
                        raise TypeError()
                    additional_property_custom_property_dates_range_type_0 = []
                    _additional_property_custom_property_dates_range_type_0 = data
                    for (
                        additional_property_custom_property_dates_range_type_0_item_data
                    ) in _additional_property_custom_property_dates_range_type_0:

                        def _parse_additional_property_custom_property_dates_range_type_0_item(
                            data: object,
                        ) -> Union[None, str]:
                            if data is None:
                                return data
                            return cast(Union[None, str], data)

                        additional_property_custom_property_dates_range_type_0_item = (
                            _parse_additional_property_custom_property_dates_range_type_0_item(
                                additional_property_custom_property_dates_range_type_0_item_data
                            )
                        )

                        additional_property_custom_property_dates_range_type_0.append(
                            additional_property_custom_property_dates_range_type_0_item
                        )

                    return additional_property_custom_property_dates_range_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, list):
                        raise TypeError()
                    additional_property_custom_property_multiselect = cast(list[str], data)

                    return additional_property_custom_property_multiselect
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, list):
                        raise TypeError()
                    additional_property_custom_property_user_multiple = cast(list[str], data)

                    return additional_property_custom_property_user_multiple
                except:  # noqa: E722
                    pass
                return cast(
                    Union[None, bool, float, int, list[Union[None, str]], list[str], str],
                    data,
                )

            additional_property = _parse_additional_property(prop_dict)

            additional_properties[prop_name] = additional_property

        task_create_custom_properties_type_0.additional_properties = additional_properties
        return task_create_custom_properties_type_0

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Union[None, bool, float, int, list[Union[None, str]], list[str], str]:
        return self.additional_properties[key]

    def __setitem__(
        self,
        key: str,
        value: Union[None, bool, float, int, list[Union[None, str]], list[str], str],
    ) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
