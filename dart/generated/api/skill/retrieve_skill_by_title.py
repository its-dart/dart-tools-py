from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.wrapped_skill import WrappedSkill
from ...types import UNSET, Response


def _get_kwargs(
    *,
    title: str,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["title"] = title

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/skills/by-title",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | WrappedSkill | None:
    if response.status_code == 200:
        response_200 = WrappedSkill.from_dict(response.json())

        return response_200

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | WrappedSkill]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    title: str,
) -> Response[Any | WrappedSkill]:
    """Retrieve a skill by title

     Retrieve a skill by its title. Skills are user-defined instructions or templates for performing
    specific task types in the workspace. Returns the skill's title and instructions if found.

    Args:
        title (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | WrappedSkill]
    """

    kwargs = _get_kwargs(
        title=title,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    title: str,
) -> Any | WrappedSkill | None:
    """Retrieve a skill by title

     Retrieve a skill by its title. Skills are user-defined instructions or templates for performing
    specific task types in the workspace. Returns the skill's title and instructions if found.

    Args:
        title (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | WrappedSkill
    """

    return sync_detailed(
        client=client,
        title=title,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    title: str,
) -> Response[Any | WrappedSkill]:
    """Retrieve a skill by title

     Retrieve a skill by its title. Skills are user-defined instructions or templates for performing
    specific task types in the workspace. Returns the skill's title and instructions if found.

    Args:
        title (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | WrappedSkill]
    """

    kwargs = _get_kwargs(
        title=title,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    title: str,
) -> Any | WrappedSkill | None:
    """Retrieve a skill by title

     Retrieve a skill by its title. Skills are user-defined instructions or templates for performing
    specific task types in the workspace. Returns the skill's title and instructions if found.

    Args:
        title (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | WrappedSkill
    """

    return (
        await asyncio_detailed(
            client=client,
            title=title,
        )
    ).parsed
