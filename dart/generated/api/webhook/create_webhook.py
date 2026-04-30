from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.wrapped_webhook import WrappedWebhook
from ...models.wrapped_webhook_create import WrappedWebhookCreate
from ...types import Response


def _get_kwargs(
    *,
    body: WrappedWebhookCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/webhooks",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, WrappedWebhook]]:
    if response.status_code == 200:
        response_200 = WrappedWebhook.from_dict(response.json())

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
) -> Response[Union[Any, WrappedWebhook]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: WrappedWebhookCreate,
) -> Response[Union[Any, WrappedWebhook]]:
    """Create a new webhook

     Create a new webhook that sends selected workspace events to a URL.

    Args:
        body (WrappedWebhookCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, WrappedWebhook]]
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
    body: WrappedWebhookCreate,
) -> Optional[Union[Any, WrappedWebhook]]:
    """Create a new webhook

     Create a new webhook that sends selected workspace events to a URL.

    Args:
        body (WrappedWebhookCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, WrappedWebhook]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: WrappedWebhookCreate,
) -> Response[Union[Any, WrappedWebhook]]:
    """Create a new webhook

     Create a new webhook that sends selected workspace events to a URL.

    Args:
        body (WrappedWebhookCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, WrappedWebhook]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: WrappedWebhookCreate,
) -> Optional[Union[Any, WrappedWebhook]]:
    """Create a new webhook

     Create a new webhook that sends selected workspace events to a URL.

    Args:
        body (WrappedWebhookCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, WrappedWebhook]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
