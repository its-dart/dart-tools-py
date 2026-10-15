from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.wrapped_doc import WrappedDoc
from ...models.wrapped_doc_create import WrappedDocCreate
from ...types import Response


def _get_kwargs(
    *,
    body: WrappedDocCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/docs",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | WrappedDoc | None:
    if response.status_code == 200:
        response_200 = WrappedDoc.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | WrappedDoc]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: WrappedDocCreate,
) -> Response[Any | WrappedDoc]:
    """Create a new doc

     Record a new doc that the user intends to write down. This will save the doc in Dart for later
    access, search, etc. By default the created doc will be in the Docs folder. More information can be
    included in the text.

    Args:
        body (WrappedDocCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | WrappedDoc]
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
    body: WrappedDocCreate,
) -> Any | WrappedDoc | None:
    """Create a new doc

     Record a new doc that the user intends to write down. This will save the doc in Dart for later
    access, search, etc. By default the created doc will be in the Docs folder. More information can be
    included in the text.

    Args:
        body (WrappedDocCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | WrappedDoc
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: WrappedDocCreate,
) -> Response[Any | WrappedDoc]:
    """Create a new doc

     Record a new doc that the user intends to write down. This will save the doc in Dart for later
    access, search, etc. By default the created doc will be in the Docs folder. More information can be
    included in the text.

    Args:
        body (WrappedDocCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | WrappedDoc]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: WrappedDocCreate,
) -> Any | WrappedDoc | None:
    """Create a new doc

     Record a new doc that the user intends to write down. This will save the doc in Dart for later
    access, search, etc. By default the created doc will be in the Docs folder. More information can be
    included in the text.

    Args:
        body (WrappedDocCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | WrappedDoc
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
