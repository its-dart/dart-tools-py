from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.wrapped_agent import WrappedAgent
from ...models.wrapped_agent_create import WrappedAgentCreate
from ...types import Response


def _get_kwargs(
    *,
    body: WrappedAgentCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/agents",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, WrappedAgent]]:
    if response.status_code == 200:
        response_200 = WrappedAgent.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, WrappedAgent]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: WrappedAgentCreate,
) -> Response[Union[Any, WrappedAgent]]:
    """Create a new agent

     Create a new agent in the workspace with a name and optional description or instructions.

    Args:
        body (WrappedAgentCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, WrappedAgent]]
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
    client: AuthenticatedClient,
    body: WrappedAgentCreate,
) -> Optional[Union[Any, WrappedAgent]]:
    """Create a new agent

     Create a new agent in the workspace with a name and optional description or instructions.

    Args:
        body (WrappedAgentCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, WrappedAgent]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: WrappedAgentCreate,
) -> Response[Union[Any, WrappedAgent]]:
    """Create a new agent

     Create a new agent in the workspace with a name and optional description or instructions.

    Args:
        body (WrappedAgentCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, WrappedAgent]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: WrappedAgentCreate,
) -> Optional[Union[Any, WrappedAgent]]:
    """Create a new agent

     Create a new agent in the workspace with a name and optional description or instructions.

    Args:
        body (WrappedAgentCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, WrappedAgent]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
