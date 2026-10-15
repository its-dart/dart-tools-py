from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.wrapped_skill import WrappedSkill
from ...models.wrapped_skill_update import WrappedSkillUpdate
from ...types import Response


def _get_kwargs(
    id: str,
    *,
    body: WrappedSkillUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/skills/{id}".format(
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | WrappedSkill | None:
    if response.status_code == 200:
        response_200 = WrappedSkill.from_dict(response.json())

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | WrappedSkill]:
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
    body: WrappedSkillUpdate,
) -> Response[Any | WrappedSkill]:
    """Update an existing skill

     Update an existing skill's title and/or instructions. Only the fields provided will be updated. The
    skill is identified by its ID in the URL.

    Args:
        id (str):
        body (WrappedSkillUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | WrappedSkill]
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
    body: WrappedSkillUpdate,
) -> Any | WrappedSkill | None:
    """Update an existing skill

     Update an existing skill's title and/or instructions. Only the fields provided will be updated. The
    skill is identified by its ID in the URL.

    Args:
        id (str):
        body (WrappedSkillUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | WrappedSkill
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
    body: WrappedSkillUpdate,
) -> Response[Any | WrappedSkill]:
    """Update an existing skill

     Update an existing skill's title and/or instructions. Only the fields provided will be updated. The
    skill is identified by its ID in the URL.

    Args:
        id (str):
        body (WrappedSkillUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | WrappedSkill]
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
    body: WrappedSkillUpdate,
) -> Any | WrappedSkill | None:
    """Update an existing skill

     Update an existing skill's title and/or instructions. Only the fields provided will be updated. The
    skill is identified by its ID in the URL.

    Args:
        id (str):
        body (WrappedSkillUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | WrappedSkill
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
