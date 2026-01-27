from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.wrapped_task import WrappedTask
from ...models.wrapped_task_update import WrappedTaskUpdate
from ...types import Response


def _get_kwargs(
    id: str,
    *,
    body: WrappedTaskUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/tasks/{id}".format(
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
    body: WrappedTaskUpdate,
) -> Response[Union[Any, WrappedTask]]:
    r"""Update an existing task

     Update properties of an existing task. For customProperties, use property NAME (not ID) as key. Get
    property names from workspace config. Example: {\"customTextProperty\": \"Some text\"}. Fields not
    provided are unchanged.

    Args:
        id (str):
        body (WrappedTaskUpdate):

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
    body: WrappedTaskUpdate,
) -> Optional[Union[Any, WrappedTask]]:
    r"""Update an existing task

     Update properties of an existing task. For customProperties, use property NAME (not ID) as key. Get
    property names from workspace config. Example: {\"customTextProperty\": \"Some text\"}. Fields not
    provided are unchanged.

    Args:
        id (str):
        body (WrappedTaskUpdate):

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
    body: WrappedTaskUpdate,
) -> Response[Union[Any, WrappedTask]]:
    r"""Update an existing task

     Update properties of an existing task. For customProperties, use property NAME (not ID) as key. Get
    property names from workspace config. Example: {\"customTextProperty\": \"Some text\"}. Fields not
    provided are unchanged.

    Args:
        id (str):
        body (WrappedTaskUpdate):

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
    body: WrappedTaskUpdate,
) -> Optional[Union[Any, WrappedTask]]:
    r"""Update an existing task

     Update properties of an existing task. For customProperties, use property NAME (not ID) as key. Get
    property names from workspace config. Example: {\"customTextProperty\": \"Some text\"}. Fields not
    provided are unchanged.

    Args:
        id (str):
        body (WrappedTaskUpdate):

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
