from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.authenticated_user import AuthenticatedUser


T = TypeVar("T", bound="Me")


@_attrs_define
class Me:
    """
    Attributes:
        is_logged_in (bool):
        user (AuthenticatedUser):
    """

    is_logged_in: bool
    user: "AuthenticatedUser"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_logged_in = self.is_logged_in

        user = self.user.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "isLoggedIn": is_logged_in,
                "user": user,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authenticated_user import AuthenticatedUser

        d = dict(src_dict)
        is_logged_in = d.pop("isLoggedIn")

        user = AuthenticatedUser.from_dict(d.pop("user"))

        me = cls(
            is_logged_in=is_logged_in,
            user=user,
        )

        me.additional_properties = d
        return me

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
