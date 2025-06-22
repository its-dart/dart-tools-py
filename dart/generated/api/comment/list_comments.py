import datetime
from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.paginated_comment_list import PaginatedCommentList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    author: Union[Unset, str] = UNSET,
    author_id: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    parent_id: Union[None, Unset, str] = UNSET,
    published_at_after: Union[Unset, datetime.datetime] = UNSET,
    published_at_before: Union[Unset, datetime.datetime] = UNSET,
    task: Union[Unset, str] = UNSET,
    task_id: Union[Unset, str] = UNSET,
    text: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["author"] = author

    params["author_id"] = author_id

    params["ids"] = ids

    params["limit"] = limit

    params["offset"] = offset

    json_parent_id: Union[None, Unset, str]
    if isinstance(parent_id, Unset):
        json_parent_id = UNSET
    else:
        json_parent_id = parent_id
    params["parent_id"] = json_parent_id

    json_published_at_after: Union[Unset, str] = UNSET
    if not isinstance(published_at_after, Unset):
        json_published_at_after = published_at_after.isoformat()
    params["published_at_after"] = json_published_at_after

    json_published_at_before: Union[Unset, str] = UNSET
    if not isinstance(published_at_before, Unset):
        json_published_at_before = published_at_before.isoformat()
    params["published_at_before"] = json_published_at_before

    params["task"] = task

    params["task_id"] = task_id

    params["text"] = text

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/comments/list",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PaginatedCommentList]:
    if response.status_code == 200:
        response_200 = PaginatedCommentList.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PaginatedCommentList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    author: Union[Unset, str] = UNSET,
    author_id: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    parent_id: Union[None, Unset, str] = UNSET,
    published_at_after: Union[Unset, datetime.datetime] = UNSET,
    published_at_before: Union[Unset, datetime.datetime] = UNSET,
    task: Union[Unset, str] = UNSET,
    task_id: Union[Unset, str] = UNSET,
    text: Union[Unset, str] = UNSET,
) -> Response[PaginatedCommentList]:
    """List all comments that the user has access to. This will return a list of comments, including the
    text, associated task ID, and others. Comments are ordered hierarchically by default.

    Args:
        author (Union[Unset, str]):
        author_id (Union[Unset, str]):
        ids (Union[Unset, str]):
        limit (Union[Unset, int]):
        offset (Union[Unset, int]):
        parent_id (Union[None, Unset, str]):
        published_at_after (Union[Unset, datetime.datetime]):
        published_at_before (Union[Unset, datetime.datetime]):
        task (Union[Unset, str]):
        task_id (Union[Unset, str]):
        text (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedCommentList]
    """

    kwargs = _get_kwargs(
        author=author,
        author_id=author_id,
        ids=ids,
        limit=limit,
        offset=offset,
        parent_id=parent_id,
        published_at_after=published_at_after,
        published_at_before=published_at_before,
        task=task,
        task_id=task_id,
        text=text,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    author: Union[Unset, str] = UNSET,
    author_id: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    parent_id: Union[None, Unset, str] = UNSET,
    published_at_after: Union[Unset, datetime.datetime] = UNSET,
    published_at_before: Union[Unset, datetime.datetime] = UNSET,
    task: Union[Unset, str] = UNSET,
    task_id: Union[Unset, str] = UNSET,
    text: Union[Unset, str] = UNSET,
) -> Optional[PaginatedCommentList]:
    """List all comments that the user has access to. This will return a list of comments, including the
    text, associated task ID, and others. Comments are ordered hierarchically by default.

    Args:
        author (Union[Unset, str]):
        author_id (Union[Unset, str]):
        ids (Union[Unset, str]):
        limit (Union[Unset, int]):
        offset (Union[Unset, int]):
        parent_id (Union[None, Unset, str]):
        published_at_after (Union[Unset, datetime.datetime]):
        published_at_before (Union[Unset, datetime.datetime]):
        task (Union[Unset, str]):
        task_id (Union[Unset, str]):
        text (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedCommentList
    """

    return sync_detailed(
        client=client,
        author=author,
        author_id=author_id,
        ids=ids,
        limit=limit,
        offset=offset,
        parent_id=parent_id,
        published_at_after=published_at_after,
        published_at_before=published_at_before,
        task=task,
        task_id=task_id,
        text=text,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    author: Union[Unset, str] = UNSET,
    author_id: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    parent_id: Union[None, Unset, str] = UNSET,
    published_at_after: Union[Unset, datetime.datetime] = UNSET,
    published_at_before: Union[Unset, datetime.datetime] = UNSET,
    task: Union[Unset, str] = UNSET,
    task_id: Union[Unset, str] = UNSET,
    text: Union[Unset, str] = UNSET,
) -> Response[PaginatedCommentList]:
    """List all comments that the user has access to. This will return a list of comments, including the
    text, associated task ID, and others. Comments are ordered hierarchically by default.

    Args:
        author (Union[Unset, str]):
        author_id (Union[Unset, str]):
        ids (Union[Unset, str]):
        limit (Union[Unset, int]):
        offset (Union[Unset, int]):
        parent_id (Union[None, Unset, str]):
        published_at_after (Union[Unset, datetime.datetime]):
        published_at_before (Union[Unset, datetime.datetime]):
        task (Union[Unset, str]):
        task_id (Union[Unset, str]):
        text (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedCommentList]
    """

    kwargs = _get_kwargs(
        author=author,
        author_id=author_id,
        ids=ids,
        limit=limit,
        offset=offset,
        parent_id=parent_id,
        published_at_after=published_at_after,
        published_at_before=published_at_before,
        task=task,
        task_id=task_id,
        text=text,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    author: Union[Unset, str] = UNSET,
    author_id: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    parent_id: Union[None, Unset, str] = UNSET,
    published_at_after: Union[Unset, datetime.datetime] = UNSET,
    published_at_before: Union[Unset, datetime.datetime] = UNSET,
    task: Union[Unset, str] = UNSET,
    task_id: Union[Unset, str] = UNSET,
    text: Union[Unset, str] = UNSET,
) -> Optional[PaginatedCommentList]:
    """List all comments that the user has access to. This will return a list of comments, including the
    text, associated task ID, and others. Comments are ordered hierarchically by default.

    Args:
        author (Union[Unset, str]):
        author_id (Union[Unset, str]):
        ids (Union[Unset, str]):
        limit (Union[Unset, int]):
        offset (Union[Unset, int]):
        parent_id (Union[None, Unset, str]):
        published_at_after (Union[Unset, datetime.datetime]):
        published_at_before (Union[Unset, datetime.datetime]):
        task (Union[Unset, str]):
        task_id (Union[Unset, str]):
        text (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedCommentList
    """

    return (
        await asyncio_detailed(
            client=client,
            author=author,
            author_id=author_id,
            ids=ids,
            limit=limit,
            offset=offset,
            parent_id=parent_id,
            published_at_after=published_at_after,
            published_at_before=published_at_before,
            task=task,
            task_id=task_id,
            text=text,
        )
    ).parsed
