from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.paginated_comment_list_meta_type_0_applied_default_filters import (
        PaginatedCommentListMetaType0AppliedDefaultFilters,
    )


T = TypeVar("T", bound="PaginatedCommentListMetaType0")


@_attrs_define
class PaginatedCommentListMetaType0:
    """
    Attributes:
        defaults_applied (Union[Unset, bool]): Whether default filters or ordering were applied to the response.
        applied_default_filters (Union[Unset, PaginatedCommentListMetaType0AppliedDefaultFilters]): The default filters
            that were applied automatically, if any.
        applied_default_sorts (Union[Unset, list[str]]): The default ordering fields that were applied automatically, if
            any.
        instructions (Union[Unset, str]): Guidance on how to disable or override default filters and ordering.
    """

    defaults_applied: Union[Unset, bool] = UNSET
    applied_default_filters: Union[Unset, "PaginatedCommentListMetaType0AppliedDefaultFilters"] = UNSET
    applied_default_sorts: Union[Unset, list[str]] = UNSET
    instructions: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        defaults_applied = self.defaults_applied

        applied_default_filters: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.applied_default_filters, Unset):
            applied_default_filters = self.applied_default_filters.to_dict()

        applied_default_sorts: Union[Unset, list[str]] = UNSET
        if not isinstance(self.applied_default_sorts, Unset):
            applied_default_sorts = self.applied_default_sorts

        instructions = self.instructions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if defaults_applied is not UNSET:
            field_dict["defaultsApplied"] = defaults_applied
        if applied_default_filters is not UNSET:
            field_dict["appliedDefaultFilters"] = applied_default_filters
        if applied_default_sorts is not UNSET:
            field_dict["appliedDefaultSorts"] = applied_default_sorts
        if instructions is not UNSET:
            field_dict["instructions"] = instructions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.paginated_comment_list_meta_type_0_applied_default_filters import (
            PaginatedCommentListMetaType0AppliedDefaultFilters,
        )

        d = dict(src_dict)
        defaults_applied = d.pop("defaultsApplied", UNSET)

        _applied_default_filters = d.pop("appliedDefaultFilters", UNSET)
        applied_default_filters: Union[Unset, PaginatedCommentListMetaType0AppliedDefaultFilters]
        if isinstance(_applied_default_filters, Unset):
            applied_default_filters = UNSET
        else:
            applied_default_filters = PaginatedCommentListMetaType0AppliedDefaultFilters.from_dict(
                _applied_default_filters
            )

        applied_default_sorts = cast(list[str], d.pop("appliedDefaultSorts", UNSET))

        instructions = d.pop("instructions", UNSET)

        paginated_comment_list_meta_type_0 = cls(
            defaults_applied=defaults_applied,
            applied_default_filters=applied_default_filters,
            applied_default_sorts=applied_default_sorts,
            instructions=instructions,
        )

        paginated_comment_list_meta_type_0.additional_properties = d
        return paginated_comment_list_meta_type_0

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
