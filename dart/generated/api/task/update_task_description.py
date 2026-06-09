from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.task_description_update import TaskDescriptionUpdate
from ...models.wrapped_task import WrappedTask
from ...types import Response


def _get_kwargs(
    id: str,
    *,
    body: TaskDescriptionUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/tasks/{id}/update-description".format(
            id=id,
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, WrappedTask]]:
    if response.status_code == 200:
        response_200 = WrappedTask.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, WrappedTask]]:
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
    body: TaskDescriptionUpdate,
) -> Response[Union[Any, WrappedTask]]:
    r"""Update a task's description with text updates

     Apply targeted text updates to a task's description; use instead of updateTask when only the
    description changes. Each update is one of: \"replace\" (swap oldText for newText),
    \"insert_before\" / \"insert_after\" (insert newText relative to anchorText), or \"delete\" (remove
    oldText), applied in order and atomically. When occurrence is omitted, the target text must be
    unique; otherwise specify occurrence (1-indexed). Preferred over a full update for long content:
    fewer tokens, and no risk of rewriting unrelated text.

    Args:
        id (str):
        body (TaskDescriptionUpdate): Payload for applying a list of targeted text updates to a
            task's description.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, WrappedTask]]
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
    body: TaskDescriptionUpdate,
) -> Optional[Union[Any, WrappedTask]]:
    r"""Update a task's description with text updates

     Apply targeted text updates to a task's description; use instead of updateTask when only the
    description changes. Each update is one of: \"replace\" (swap oldText for newText),
    \"insert_before\" / \"insert_after\" (insert newText relative to anchorText), or \"delete\" (remove
    oldText), applied in order and atomically. When occurrence is omitted, the target text must be
    unique; otherwise specify occurrence (1-indexed). Preferred over a full update for long content:
    fewer tokens, and no risk of rewriting unrelated text.

    Args:
        id (str):
        body (TaskDescriptionUpdate): Payload for applying a list of targeted text updates to a
            task's description.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, WrappedTask]
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
    body: TaskDescriptionUpdate,
) -> Response[Union[Any, WrappedTask]]:
    r"""Update a task's description with text updates

     Apply targeted text updates to a task's description; use instead of updateTask when only the
    description changes. Each update is one of: \"replace\" (swap oldText for newText),
    \"insert_before\" / \"insert_after\" (insert newText relative to anchorText), or \"delete\" (remove
    oldText), applied in order and atomically. When occurrence is omitted, the target text must be
    unique; otherwise specify occurrence (1-indexed). Preferred over a full update for long content:
    fewer tokens, and no risk of rewriting unrelated text.

    Args:
        id (str):
        body (TaskDescriptionUpdate): Payload for applying a list of targeted text updates to a
            task's description.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, WrappedTask]]
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
    body: TaskDescriptionUpdate,
) -> Optional[Union[Any, WrappedTask]]:
    r"""Update a task's description with text updates

     Apply targeted text updates to a task's description; use instead of updateTask when only the
    description changes. Each update is one of: \"replace\" (swap oldText for newText),
    \"insert_before\" / \"insert_after\" (insert newText relative to anchorText), or \"delete\" (remove
    oldText), applied in order and atomically. When occurrence is omitted, the target text must be
    unique; otherwise specify occurrence (1-indexed). Preferred over a full update for long content:
    fewer tokens, and no risk of rewriting unrelated text.

    Args:
        id (str):
        body (TaskDescriptionUpdate): Payload for applying a list of targeted text updates to a
            task's description.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, WrappedTask]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
