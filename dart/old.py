#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""These are legacy components that still rely on private API, moved out of dart.py."""

# Required for type hinting compatibility when using Python 3.9
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Union

import httpx

from .dart import (
    Dart,
    _auth_failure_exit,
    _handle_request_errors,
    _log,
    _make_id,
    _unknown_failure_exit,
)
from .exception import DartException

_CREATE_TRANSACTION_URL_FRAG = "/transactions/create"
_LIST_DARTBOARDS_URL_FRAG = "/dartboards"
_LIST_FOLDERS_URL_FRAG = "/folders"
_REPLICATE_DARTBOARD_URL_FRAG_FMT = "/dartboards/replicate/{dartboard_id}"
_REPLICATE_SPACE_URL_FRAG_FMT = "/spaces/replicate/{space_id}"


def _get_space_url(host: str, space_id: str) -> str:
    return f"{host}/s/{space_id}"


def _get_dartboard_url(host: str, dartboard_id: str) -> str:
    return f"{host}/d/{dartboard_id}"


def _get_folder_url(host: str, folder_id: str) -> str:
    return f"{host}/f/{folder_id}"


def _handle_api_errors(fn: Callable[..., httpx.Response]) -> Callable[..., httpx.Response]:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        response = fn(*args, **kwargs)
        if response.status_code in {401, 403}:
            _auth_failure_exit()
        return response

    return wrapper


def _parse_transaction_response_and_maybe_exit(response: dict, model_kind: str, model_id: str) -> Any:
    if (
        response is None
        or "results" not in response
        or not response["results"]
        or not response["results"][0]["success"]
    ):
        _unknown_failure_exit()
    models = response["results"][0]["models"][f"{model_kind}s"]
    model = next((e for e in models if e["duid"] == model_id), None)
    if model is None:
        _unknown_failure_exit()
    return model


class DartOld(Dart):
    @_handle_api_errors
    @_handle_request_errors
    def transact(self, operations: list[dict], kind: str) -> httpx.Response:
        transaction = {
            "duid": _make_id(),
            "kind": kind,
            "operations": operations,
        }
        request_body = {
            "client_duid": self.get_client_id(),
            "items": [transaction],
        }
        return self._private_api.get_httpx_client().post(_CREATE_TRANSACTION_URL_FRAG, json=request_body)

    @_handle_api_errors
    @_handle_request_errors
    def get(self, url_frag, *args, **kwargs) -> httpx.Response:
        return self._private_api.get_httpx_client().get(url_frag, *args, **kwargs)

    @_handle_api_errors
    @_handle_request_errors
    def post(self, url_frag, *args, **kwargs) -> httpx.Response:
        return self._private_api.get_httpx_client().post(url_frag, *args, **kwargs)


def replicate_space(
    space_id: str,
    *,
    title: Union[str, None] = None,
    abrev: Union[str, None] = None,
    color_hex: Union[str, None] = None,
    accessible_by_team: Union[bool, None] = None,
    accessor_duids: Union[list[str], None] = None,
) -> str:
    dart = DartOld()
    content = {}
    if title is not None:
        content["title"] = title
    if abrev is not None:
        content["abrev"] = abrev
    if color_hex is not None:
        content["colorHex"] = color_hex
    if accessible_by_team is not None:
        content["accessibleByTeam"] = accessible_by_team
    if accessor_duids is not None:
        content["accessorIds"] = accessor_duids
    response = dart.post(_REPLICATE_SPACE_URL_FRAG_FMT.format(space_id=space_id), json=content)
    space_id = response.json()["duid"]

    _log(f"Replicated space at {_get_space_url(dart.get_base_url(), space_id)}")
    _log("Done.")
    return space_id


def get_dartboards(space_id: str, include_special: bool = False) -> list[dict]:
    dart = DartOld()

    response = dart.get(_LIST_DARTBOARDS_URL_FRAG, params={"space_duid": space_id, "limit": 100})
    response_json = response.json()
    dartboards = response_json["results"] if response_json is not None else []
    while response_json.get("next") is not None:
        response = dart.get(response_json["next"])
        response_json = response.json()
        if response_json is not None and "results" in response_json:
            dartboards.extend(response_json["results"])

    if not include_special:
        dartboards = [e for e in dartboards if e["kind"] == "Custom"]

    _log(f"Got {len(dartboards)} dartboards")
    _log("Done.")
    return dartboards


def replicate_dartboard(dartboard_id: str, *, title: Union[str, None] = None) -> str:
    dart = DartOld()
    content = {}
    if title is not None:
        content["title"] = title
    response = dart.post(_REPLICATE_DARTBOARD_URL_FRAG_FMT.format(dartboard_id=dartboard_id), json=content)
    dartboard_id = response.json()["duid"]

    _log(f"Replicated dartboard at {_get_dartboard_url(dart.get_base_url(), dartboard_id)}")
    _log("Done.")
    return dartboard_id


def update_dartboard(dartboard_id: str, *, title: Union[str, None] = None, color_hex: Union[str, None] = None) -> dict:
    dart = DartOld()
    dartboard_update = {}

    if title is not None:
        dartboard_update["title"] = title
    if color_hex is not None:
        dartboard_update["color_hex"] = color_hex

    if not dartboard_update:
        raise DartException("At least one of 'title' or 'color_hex' must be provided to update a dartboard.")

    dartboard_update["duid"] = dartboard_id
    dartboard_update_op = {
        "model": "dartboard",
        "kind": "update",
        "data": dartboard_update,
    }
    response = dart.transact([dartboard_update_op], "dartboard_update")
    response_json = response.json()
    dartboard = _parse_transaction_response_and_maybe_exit(response_json, "dartboard", dartboard_id)

    _log(f"Updated dartboard {dartboard['title']} at {_get_dartboard_url(dart.get_base_url(), dartboard['duid'])}")
    _log("Done.")
    return dartboard


def get_folders(space_id: str, *, include_special: Union[bool, None] = False) -> list[dict]:
    dart = DartOld()

    response = dart.get(_LIST_FOLDERS_URL_FRAG, params={"space_duid": space_id, "limit": 50})
    response_json = response.json()
    folders = response_json["results"] if response_json is not None else []
    while response_json.get("next") is not None:
        response = dart.get(response_json["next"])
        response_json = response.json()
        if response_json is not None and "results" in response_json:
            folders.extend(response_json["results"])

    if not include_special:
        folders = [e for e in folders if e["kind"] == "Other"]

    _log(f"Got {len(folders)} folders")
    _log("Done.")
    return folders


def update_folder(folder_id: str, *, title: Union[str, None] = None, color_hex: Union[str, None] = None) -> dict:
    dart = DartOld()
    folder_update = {}

    if title is not None:
        folder_update["title"] = title
    if color_hex is not None:
        folder_update["color_hex"] = color_hex

    if not folder_update:
        raise DartException("At least one of 'title' or 'color_hex' must be provided to update a folder.")

    folder_update["duid"] = folder_id
    folder_update_op = {
        "model": "folder",
        "kind": "update",
        "data": folder_update,
    }
    response = dart.transact([folder_update_op], "folder_update")
    response_json = response.json()
    folder = _parse_transaction_response_and_maybe_exit(response_json, "folder", folder_id)

    _log(f"Updated folder {folder['title']} at {_get_folder_url(dart.get_base_url(), folder['duid'])}")
    _log("Done.")
    return folder
