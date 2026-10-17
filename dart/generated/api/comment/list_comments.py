import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.list_comments_o_item import ListCommentsOItem
from ...models.paginated_comment_list import PaginatedCommentList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    author: str | Unset = UNSET,
    author_id: str | Unset = UNSET,
    ids: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    o: list[ListCommentsOItem] | Unset = UNSET,
    offset: int | Unset = UNSET,
    parent_id: str | Unset = UNSET,
    published_at: datetime.datetime | Unset = UNSET,
    published_at_after: datetime.datetime | Unset = UNSET,
    published_at_before: datetime.datetime | Unset = UNSET,
    task: str | Unset = UNSET,
    task_id: str,
    text: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["author"] = author

    params["author_id"] = author_id

    params["ids"] = ids

    params["limit"] = limit

    json_o: list[str] | Unset = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["offset"] = offset

    params["parent_id"] = parent_id

    json_published_at: str | Unset = UNSET
    if not isinstance(published_at, Unset):
        json_published_at = published_at.isoformat()
    params["published_at"] = json_published_at

    json_published_at_after: str | Unset = UNSET
    if not isinstance(published_at_after, Unset):
        json_published_at_after = published_at_after.isoformat()
    params["published_at_after"] = json_published_at_after

    json_published_at_before: str | Unset = UNSET
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


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> PaginatedCommentList | None:
    if response.status_code == 200:
        response_200 = PaginatedCommentList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedCommentList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    author: str | Unset = UNSET,
    author_id: str | Unset = UNSET,
    ids: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    o: list[ListCommentsOItem] | Unset = UNSET,
    offset: int | Unset = UNSET,
    parent_id: str | Unset = UNSET,
    published_at: datetime.datetime | Unset = UNSET,
    published_at_after: datetime.datetime | Unset = UNSET,
    published_at_before: datetime.datetime | Unset = UNSET,
    task: str | Unset = UNSET,
    task_id: str,
    text: str | Unset = UNSET,
) -> Response[PaginatedCommentList]:
    """List comments for a task with filtering options. Filter by author, text content, or date range. Sort
    by date or hierarchical thread order. Task ID required. Supports pagination.

    Args:
        author (str | Unset):
        author_id (str | Unset):
        ids (str | Unset):
        limit (int | Unset):
        o (list[ListCommentsOItem] | Unset):
        offset (int | Unset):
        parent_id (str | Unset):
        published_at (datetime.datetime | Unset):
        published_at_after (datetime.datetime | Unset):
        published_at_before (datetime.datetime | Unset):
        task (str | Unset):
        task_id (str):
        text (str | Unset):

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
    client: AuthenticatedClient,
    author: str | Unset = UNSET,
    author_id: str | Unset = UNSET,
    ids: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    o: list[ListCommentsOItem] | Unset = UNSET,
    offset: int | Unset = UNSET,
    parent_id: str | Unset = UNSET,
    published_at: datetime.datetime | Unset = UNSET,
    published_at_after: datetime.datetime | Unset = UNSET,
    published_at_before: datetime.datetime | Unset = UNSET,
    task: str | Unset = UNSET,
    task_id: str,
    text: str | Unset = UNSET,
) -> PaginatedCommentList | None:
    """List comments for a task with filtering options. Filter by author, text content, or date range. Sort
    by date or hierarchical thread order. Task ID required. Supports pagination.

    Args:
        author (str | Unset):
        author_id (str | Unset):
        ids (str | Unset):
        limit (int | Unset):
        o (list[ListCommentsOItem] | Unset):
        offset (int | Unset):
        parent_id (str | Unset):
        published_at (datetime.datetime | Unset):
        published_at_after (datetime.datetime | Unset):
        published_at_before (datetime.datetime | Unset):
        task (str | Unset):
        task_id (str):
        text (str | Unset):

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
    client: AuthenticatedClient,
    author: str | Unset = UNSET,
    author_id: str | Unset = UNSET,
    ids: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    o: list[ListCommentsOItem] | Unset = UNSET,
    offset: int | Unset = UNSET,
    parent_id: str | Unset = UNSET,
    published_at: datetime.datetime | Unset = UNSET,
    published_at_after: datetime.datetime | Unset = UNSET,
    published_at_before: datetime.datetime | Unset = UNSET,
    task: str | Unset = UNSET,
    task_id: str,
    text: str | Unset = UNSET,
) -> Response[PaginatedCommentList]:
    """List comments for a task with filtering options. Filter by author, text content, or date range. Sort
    by date or hierarchical thread order. Task ID required. Supports pagination.

    Args:
        author (str | Unset):
        author_id (str | Unset):
        ids (str | Unset):
        limit (int | Unset):
        o (list[ListCommentsOItem] | Unset):
        offset (int | Unset):
        parent_id (str | Unset):
        published_at (datetime.datetime | Unset):
        published_at_after (datetime.datetime | Unset):
        published_at_before (datetime.datetime | Unset):
        task (str | Unset):
        task_id (str):
        text (str | Unset):

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
    client: AuthenticatedClient,
    author: str | Unset = UNSET,
    author_id: str | Unset = UNSET,
    ids: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    o: list[ListCommentsOItem] | Unset = UNSET,
    offset: int | Unset = UNSET,
    parent_id: str | Unset = UNSET,
    published_at: datetime.datetime | Unset = UNSET,
    published_at_after: datetime.datetime | Unset = UNSET,
    published_at_before: datetime.datetime | Unset = UNSET,
    task: str | Unset = UNSET,
    task_id: str,
    text: str | Unset = UNSET,
) -> PaginatedCommentList | None:
    """List comments for a task with filtering options. Filter by author, text content, or date range. Sort
    by date or hierarchical thread order. Task ID required. Supports pagination.

    Args:
        author (str | Unset):
        author_id (str | Unset):
        ids (str | Unset):
        limit (int | Unset):
        o (list[ListCommentsOItem] | Unset):
        offset (int | Unset):
        parent_id (str | Unset):
        published_at (datetime.datetime | Unset):
        published_at_after (datetime.datetime | Unset):
        published_at_before (datetime.datetime | Unset):
        task (str | Unset):
        task_id (str):
        text (str | Unset):

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
