from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define

T = TypeVar("T", bound="TimeTrackingEntry")


@_attrs_define
class TimeTrackingEntry:
    """
    Attributes:
        user_duid (str):
        started_at (str):
        finished_at (Union[None, str]):
    """

    user_duid: str
    started_at: str
    finished_at: Union[None, str]

    def to_dict(self) -> dict[str, Any]:
        user_duid = self.user_duid

        started_at = self.started_at

        finished_at: Union[None, str]
        finished_at = self.finished_at

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "userDuid": user_duid,
                "startedAt": started_at,
                "finishedAt": finished_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_duid = d.pop("userDuid")

        started_at = d.pop("startedAt")

        def _parse_finished_at(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        finished_at = _parse_finished_at(d.pop("finishedAt"))

        time_tracking_entry = cls(
            user_duid=user_duid,
            started_at=started_at,
            finished_at=finished_at,
        )

        return time_tracking_entry
