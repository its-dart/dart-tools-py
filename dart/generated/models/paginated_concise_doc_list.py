from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.concise_doc import ConciseDoc
    from ..models.paginated_concise_doc_list_meta_type_0 import (
        PaginatedConciseDocListMetaType0,
    )


T = TypeVar("T", bound="PaginatedConciseDocList")


@_attrs_define
class PaginatedConciseDocList:
    """
    Attributes:
        count (int):  Example: 123.
        results (list['ConciseDoc']):
        next_ (Union[None, Unset, str]):  Example: http://api.example.org/accounts/?offset=400&limit=100.
        previous (Union[None, Unset, str]):  Example: http://api.example.org/accounts/?offset=200&limit=100.
        meta (Union['PaginatedConciseDocListMetaType0', None, Unset]):
    """

    count: int
    results: list["ConciseDoc"]
    next_: Union[None, Unset, str] = UNSET
    previous: Union[None, Unset, str] = UNSET
    meta: Union["PaginatedConciseDocListMetaType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.paginated_concise_doc_list_meta_type_0 import (
            PaginatedConciseDocListMetaType0,
        )

        count = self.count

        results = []
        for results_item_data in self.results:
            results_item = results_item_data.to_dict()
            results.append(results_item)

        next_: Union[None, Unset, str]
        if isinstance(self.next_, Unset):
            next_ = UNSET
        else:
            next_ = self.next_

        previous: Union[None, Unset, str]
        if isinstance(self.previous, Unset):
            previous = UNSET
        else:
            previous = self.previous

        meta: Union[None, Unset, dict[str, Any]]
        if isinstance(self.meta, Unset):
            meta = UNSET
        elif isinstance(self.meta, PaginatedConciseDocListMetaType0):
            meta = self.meta.to_dict()
        else:
            meta = self.meta

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "count": count,
                "results": results,
            }
        )
        if next_ is not UNSET:
            field_dict["next"] = next_
        if previous is not UNSET:
            field_dict["previous"] = previous
        if meta is not UNSET:
            field_dict["meta"] = meta

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.concise_doc import ConciseDoc
        from ..models.paginated_concise_doc_list_meta_type_0 import (
            PaginatedConciseDocListMetaType0,
        )

        d = dict(src_dict)
        count = d.pop("count")

        results = []
        _results = d.pop("results")
        for results_item_data in _results:
            results_item = ConciseDoc.from_dict(results_item_data)

            results.append(results_item)

        def _parse_next_(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        next_ = _parse_next_(d.pop("next", UNSET))

        def _parse_previous(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        previous = _parse_previous(d.pop("previous", UNSET))

        def _parse_meta(
            data: object,
        ) -> Union["PaginatedConciseDocListMetaType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                meta_type_0 = PaginatedConciseDocListMetaType0.from_dict(data)

                return meta_type_0
            except:  # noqa: E722
                pass
            return cast(Union["PaginatedConciseDocListMetaType0", None, Unset], data)

        meta = _parse_meta(d.pop("meta", UNSET))

        paginated_concise_doc_list = cls(
            count=count,
            results=results,
            next_=next_,
            previous=previous,
            meta=meta,
        )

        paginated_concise_doc_list.additional_properties = d
        return paginated_concise_doc_list

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
