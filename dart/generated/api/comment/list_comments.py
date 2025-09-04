import datetime
from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.list_comments_o_item import ListCommentsOItem
from ...models.paginated_comment_list import PaginatedCommentList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    author: Union[Unset, str] = UNSET,
    author_id: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    o: Union[Unset, list[ListCommentsOItem]] = UNSET,
    offset: Union[Unset, int] = UNSET,
    parent_id: Union[Unset, str] = UNSET,
    published_at: Union[Unset, datetime.datetime] = UNSET,
    published_at_after: Union[Unset, datetime.datetime] = UNSET,
    published_at_before: Union[Unset, datetime.datetime] = UNSET,
    task: Union[Unset, str] = UNSET,
    task_id: str,
    text: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["author"] = author

    params["author_id"] = author_id

    params["ids"] = ids

    params["limit"] = limit

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["offset"] = offset

    params["parent_id"] = parent_id

    json_published_at: Union[Unset, str] = UNSET
    if not isinstance(published_at, Unset):
        json_published_at = published_at.isoformat()
    params["published_at"] = json_published_at

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
    o: Union[Unset, list[ListCommentsOItem]] = UNSET,
    offset: Union[Unset, int] = UNSET,
    parent_id: Union[Unset, str] = UNSET,
    published_at: Union[Unset, datetime.datetime] = UNSET,
    published_at_after: Union[Unset, datetime.datetime] = UNSET,
    published_at_before: Union[Unset, datetime.datetime] = UNSET,
    task: Union[Unset, str] = UNSET,
    task_id: str,
    text: Union[Unset, str] = UNSET,
) -> Response[PaginatedCommentList]:
    """List comments for a task with filtering options. Filter by author, text content, or date range. Sort
    by date or hierarchical thread order. Task ID required. Supports pagination.

    Args:
        author (Union[Unset, str]):
        author_id (Union[Unset, str]):
        ids (Union[Unset, str]):
        limit (Union[Unset, int]):
        o (Union[Unset, list[ListCommentsOItem]]):
        offset (Union[Unset, int]):
        parent_id (Union[Unset, str]):
        published_at (Union[Unset, datetime.datetime]):
        published_at_after (Union[Unset, datetime.datetime]):
        published_at_before (Union[Unset, datetime.datetime]):
        task (Union[Unset, str]):
        task_id (str):
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
        o=o,
        offset=offset,
        parent_id=parent_id,
        published_at=published_at,
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
    o: Union[Unset, list[ListCommentsOItem]] = UNSET,
    offset: Union[Unset, int] = UNSET,
    parent_id: Union[Unset, str] = UNSET,
    published_at: Union[Unset, datetime.datetime] = UNSET,
    published_at_after: Union[Unset, datetime.datetime] = UNSET,
    published_at_before: Union[Unset, datetime.datetime] = UNSET,
    task: Union[Unset, str] = UNSET,
    task_id: str,
    text: Union[Unset, str] = UNSET,
) -> Optional[PaginatedCommentList]:
    """List comments for a task with filtering options. Filter by author, text content, or date range. Sort
    by date or hierarchical thread order. Task ID required. Supports pagination.

    Args:
        author (Union[Unset, str]):
        author_id (Union[Unset, str]):
        ids (Union[Unset, str]):
        limit (Union[Unset, int]):
        o (Union[Unset, list[ListCommentsOItem]]):
        offset (Union[Unset, int]):
        parent_id (Union[Unset, str]):
        published_at (Union[Unset, datetime.datetime]):
        published_at_after (Union[Unset, datetime.datetime]):
        published_at_before (Union[Unset, datetime.datetime]):
        task (Union[Unset, str]):
        task_id (str):
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
        o=o,
        offset=offset,
        parent_id=parent_id,
        published_at=published_at,
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
    o: Union[Unset, list[ListCommentsOItem]] = UNSET,
    offset: Union[Unset, int] = UNSET,
    parent_id: Union[Unset, str] = UNSET,
    published_at: Union[Unset, datetime.datetime] = UNSET,
    published_at_after: Union[Unset, datetime.datetime] = UNSET,
    published_at_before: Union[Unset, datetime.datetime] = UNSET,
    task: Union[Unset, str] = UNSET,
    task_id: str,
    text: Union[Unset, str] = UNSET,
) -> Response[PaginatedCommentList]:
    """List comments for a task with filtering options. Filter by author, text content, or date range. Sort
    by date or hierarchical thread order. Task ID required. Supports pagination.

    Args:
        author (Union[Unset, str]):
        author_id (Union[Unset, str]):
        ids (Union[Unset, str]):
        limit (Union[Unset, int]):
        o (Union[Unset, list[ListCommentsOItem]]):
        offset (Union[Unset, int]):
        parent_id (Union[Unset, str]):
        published_at (Union[Unset, datetime.datetime]):
        published_at_after (Union[Unset, datetime.datetime]):
        published_at_before (Union[Unset, datetime.datetime]):
        task (Union[Unset, str]):
        task_id (str):
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
        o=o,
        offset=offset,
        parent_id=parent_id,
        published_at=published_at,
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
    o: Union[Unset, list[ListCommentsOItem]] = UNSET,
    offset: Union[Unset, int] = UNSET,
    parent_id: Union[Unset, str] = UNSET,
    published_at: Union[Unset, datetime.datetime] = UNSET,
    published_at_after: Union[Unset, datetime.datetime] = UNSET,
    published_at_before: Union[Unset, datetime.datetime] = UNSET,
    task: Union[Unset, str] = UNSET,
    task_id: str,
    text: Union[Unset, str] = UNSET,
) -> Optional[PaginatedCommentList]:
    """List comments for a task with filtering options. Filter by author, text content, or date range. Sort
    by date or hierarchical thread order. Task ID required. Supports pagination.

    Args:
        author (Union[Unset, str]):
        author_id (Union[Unset, str]):
        ids (Union[Unset, str]):
        limit (Union[Unset, int]):
        o (Union[Unset, list[ListCommentsOItem]]):
        offset (Union[Unset, int]):
        parent_id (Union[Unset, str]):
        published_at (Union[Unset, datetime.datetime]):
        published_at_after (Union[Unset, datetime.datetime]):
        published_at_before (Union[Unset, datetime.datetime]):
        task (Union[Unset, str]):
        task_id (str):
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
            o=o,
            offset=offset,
            parent_id=parent_id,
            published_at=published_at,
            published_at_after=published_at_after,
            published_at_before=published_at_before,
            task=task,
            task_id=task_id,
            text=text,
        )
    ).parsed
