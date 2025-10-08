from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TaskTimeTrackingCreate")


@_attrs_define
class TaskTimeTrackingCreate:
    """
    Attributes:
        user (Union[None, str]): The name or email of the user to attribute the tracked time to or null to use the
            current user.
        started_at (str): The start timestamp for the tracked time entry in ISO 8601 format.
        finished_at (str): The end timestamp for the tracked time entry in ISO 8601 format. Must be after the start
            time.
    """

    user: Union[None, str]
    started_at: str
    finished_at: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user: Union[None, str]
        user = self.user

        started_at = self.started_at

        finished_at = self.finished_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user": user,
                "startedAt": started_at,
                "finishedAt": finished_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_user(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        user = _parse_user(d.pop("user"))

        started_at = d.pop("startedAt")

        finished_at = d.pop("finishedAt")

        task_time_tracking_create = cls(
            user=user,
            started_at=started_at,
            finished_at=finished_at,
        )

        task_time_tracking_create.additional_properties = d
        return task_time_tracking_create

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
