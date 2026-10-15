from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.task_move import TaskMove
from ...models.wrapped_task import WrappedTask
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    body: TaskMove | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/tasks/{id}/move".format(
            id=quote(str(id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | WrappedTask | None:
    if response.status_code == 200:
        response_200 = WrappedTask.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | WrappedTask]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    body: TaskMove | Unset = UNSET,
) -> Response[Any | WrappedTask]:
    """Move a task within its dartboard

     Move a task to a specific position within results sorted by the order field. Use afterTaskId to
    place the task after a specific task, or beforeTaskId to place it before one.

    Args:
        id (str):
        body (TaskMove | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | WrappedTask]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient,
    body: TaskMove | Unset = UNSET,
) -> Any | WrappedTask | None:
    """Move a task within its dartboard

     Move a task to a specific position within results sorted by the order field. Use afterTaskId to
    place the task after a specific task, or beforeTaskId to place it before one.

    Args:
        id (str):
        body (TaskMove | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | WrappedTask
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    body: TaskMove | Unset = UNSET,
) -> Response[Any | WrappedTask]:
    """Move a task within its dartboard

     Move a task to a specific position within results sorted by the order field. Use afterTaskId to
    place the task after a specific task, or beforeTaskId to place it before one.

    Args:
        id (str):
        body (TaskMove | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | WrappedTask]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    body: TaskMove | Unset = UNSET,
) -> Any | WrappedTask | None:
    """Move a task within its dartboard

     Move a task to a specific position within results sorted by the order field. Use afterTaskId to
    place the task after a specific task, or beforeTaskId to place it before one.

    Args:
        id (str):
        body (TaskMove | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | WrappedTask
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
