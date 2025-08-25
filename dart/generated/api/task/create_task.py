from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.wrapped_task import WrappedTask
from ...models.wrapped_task_create import WrappedTaskCreate
from ...types import Response


def _get_kwargs(
    *,
    body: WrappedTaskCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/tasks",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[WrappedTask]:
    if response.status_code == 200:
        response_200 = WrappedTask.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[WrappedTask]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: WrappedTaskCreate,
) -> Response[WrappedTask]:
    """Create a new task

     Record a new task that the user intends to do. By default the task will be assigned to the current
    user, have an unstarted status, have no parent, and be in the default dartboard. More information
    can be included in the description.

    Args:
        body (WrappedTaskCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WrappedTask]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: WrappedTaskCreate,
) -> Optional[WrappedTask]:
    """Create a new task

     Record a new task that the user intends to do. By default the task will be assigned to the current
    user, have an unstarted status, have no parent, and be in the default dartboard. More information
    can be included in the description.

    Args:
        body (WrappedTaskCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WrappedTask
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: WrappedTaskCreate,
) -> Response[WrappedTask]:
    """Create a new task

     Record a new task that the user intends to do. By default the task will be assigned to the current
    user, have an unstarted status, have no parent, and be in the default dartboard. More information
    can be included in the description.

    Args:
        body (WrappedTaskCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WrappedTask]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: WrappedTaskCreate,
) -> Optional[WrappedTask]:
    """Create a new task

     Record a new task that the user intends to do. By default the task will be assigned to the current
    user, have an unstarted status, have no parent, and be in the default dartboard. More information
    can be included in the description.

    Args:
        body (WrappedTaskCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WrappedTask
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
