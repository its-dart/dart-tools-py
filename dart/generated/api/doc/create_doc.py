from http import HTTPStatus
from typing import Any, Optional, Union, cast

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

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, WrappedDoc]]:
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


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, WrappedDoc]]:
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
) -> Response[Union[Any, WrappedDoc]]:
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
        Response[Union[Any, WrappedDoc]]
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
) -> Optional[Union[Any, WrappedDoc]]:
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
        Union[Any, WrappedDoc]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: WrappedDocCreate,
) -> Response[Union[Any, WrappedDoc]]:
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
        Response[Union[Any, WrappedDoc]]
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
) -> Optional[Union[Any, WrappedDoc]]:
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
        Union[Any, WrappedDoc]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
