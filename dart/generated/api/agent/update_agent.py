from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.wrapped_agent import WrappedAgent
from ...models.wrapped_agent_update import WrappedAgentUpdate
from ...types import Response


def _get_kwargs(
    id: str,
    *,
    body: WrappedAgentUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/agents/{id}".format(
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | WrappedAgent | None:
    if response.status_code == 200:
        response_200 = WrappedAgent.from_dict(response.json())

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | WrappedAgent]:
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
    body: WrappedAgentUpdate,
) -> Response[Any | WrappedAgent]:
    """Update an agent

     Update an existing agent. The agent ID and fields to change. Use the same ID as the path id; omitted
    top-level fields keep their current values.

    Args:
        id (str):
        body (WrappedAgentUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | WrappedAgent]
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
    body: WrappedAgentUpdate,
) -> Any | WrappedAgent | None:
    """Update an agent

     Update an existing agent. The agent ID and fields to change. Use the same ID as the path id; omitted
    top-level fields keep their current values.

    Args:
        id (str):
        body (WrappedAgentUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | WrappedAgent
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
    body: WrappedAgentUpdate,
) -> Response[Any | WrappedAgent]:
    """Update an agent

     Update an existing agent. The agent ID and fields to change. Use the same ID as the path id; omitted
    top-level fields keep their current values.

    Args:
        id (str):
        body (WrappedAgentUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | WrappedAgent]
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
    body: WrappedAgentUpdate,
) -> Any | WrappedAgent | None:
    """Update an agent

     Update an existing agent. The agent ID and fields to change. Use the same ID as the path id; omitted
    top-level fields keep their current values.

    Args:
        id (str):
        body (WrappedAgentUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | WrappedAgent
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
