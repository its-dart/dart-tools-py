#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import mimetypes
import os
import random
import string

import requests

_DART_TOKEN = os.environ.get("DART_TOKEN")

_BASE_URL = "https://app.dartai.com"
_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + _DART_TOKEN,
}

_DUID_CHARS = string.ascii_lowercase + string.ascii_uppercase + string.digits


def _make_duid() -> str:
    return "".join(random.choices(_DUID_CHARS, k=12))


def _get_task_id(task_title: str) -> str:
    response = requests.get(
        f"{_BASE_URL}/api/v0/public/tasks/list",
        params={"title": task_title},
        headers=_HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["results"][0]["id"]


def _create_presigned_url_config(file_name: str, attachment_id: str) -> dict:
    response = requests.post(
        f"{_BASE_URL}/api/v0/create-presigned-url",
        json={
            "kind": "attachment",
            "filename": file_name,
            "entityDuid": attachment_id,
        },
        headers=_HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def _make_attachment(task_id: str, attachment_id: str, file_name: str, file_type: str, file_url: str):
    response = requests.post(
        f"{_BASE_URL}/api/v0/transactions/create",
        json={
            "items": [
                {
                    "kind": "task_update",
                    "operations": [
                        {
                            "model": "attachment",
                            "kind": "create",
                            "data": {
                                "duid": attachment_id,
                                "order": _make_duid(),
                                "name": file_name,
                                "kind": file_type,
                                "filePath": file_url,
                            },
                        },
                        {
                            "model": "task",
                            "kind": "update_list_add",
                            "data": {
                                "duid": task_id,
                                "attachmentDuids": [attachment_id],
                            },
                        },
                    ],
                },
            ]
        },
        headers=_HEADERS,
        timeout=10,
    )
    response.raise_for_status()


def _get_file(file_url: str) -> bytes:
    response = requests.get(file_url, timeout=10)
    response.raise_for_status()
    return response.content


def _upload_file(file: bytes, presigned_url: str, signed_headers: dict):
    response = requests.put(presigned_url, data=file, headers=signed_headers, timeout=10)
    response.raise_for_status()


def upload_attachment(task_title: str, file_name: str, file_url: str) -> str:
    file_type = mimetypes.guess_type(file_url)[0] or "application/octet-stream"
    task_id = _get_task_id(task_title)
    attachment_id = _make_duid()
    presigned_url_config = _create_presigned_url_config(file_name, attachment_id)
    _make_attachment(task_id, attachment_id, file_name, file_type, presigned_url_config["filePath"])
    file = _get_file(file_url)
    _upload_file(
        file,
        presigned_url_config["presignedUrl"],
        presigned_url_config["signedHeaders"],
    )
    return attachment_id
