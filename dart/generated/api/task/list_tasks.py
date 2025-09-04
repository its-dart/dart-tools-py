import datetime
from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.paginated_concise_task_list import PaginatedConciseTaskList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    assignee: Union[Unset, str] = UNSET,
    assignee_id: Union[Unset, str] = UNSET,
    dartboard: Union[Unset, str] = UNSET,
    dartboard_id: Union[Unset, str] = UNSET,
    description: Union[Unset, str] = UNSET,
    due_at: Union[Unset, datetime.datetime] = UNSET,
    due_at_after: Union[Unset, datetime.datetime] = UNSET,
    due_at_before: Union[Unset, datetime.datetime] = UNSET,
    ids: Union[Unset, str] = UNSET,
    in_trash: Union[Unset, bool] = UNSET,
    is_completed: Union[Unset, bool] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    parent_id: Union[Unset, str] = UNSET,
    priority: Union[Unset, str] = UNSET,
    size: Union[Unset, int] = UNSET,
    start_at: Union[Unset, datetime.datetime] = UNSET,
    start_at_after: Union[Unset, datetime.datetime] = UNSET,
    start_at_before: Union[Unset, datetime.datetime] = UNSET,
    status: Union[Unset, str] = UNSET,
    status_id: Union[Unset, str] = UNSET,
    tag: Union[Unset, str] = UNSET,
    tag_id: Union[Unset, str] = UNSET,
    title: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,
    type_id: Union[Unset, str] = UNSET,
    view: Union[Unset, str] = UNSET,
    view_id: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["assignee"] = assignee

    params["assignee_id"] = assignee_id

    params["dartboard"] = dartboard

    params["dartboard_id"] = dartboard_id

    params["description"] = description

    json_due_at: Union[Unset, str] = UNSET
    if not isinstance(due_at, Unset):
        json_due_at = due_at.isoformat()
    params["due_at"] = json_due_at

    json_due_at_after: Union[Unset, str] = UNSET
    if not isinstance(due_at_after, Unset):
        json_due_at_after = due_at_after.isoformat()
    params["due_at_after"] = json_due_at_after

    json_due_at_before: Union[Unset, str] = UNSET
    if not isinstance(due_at_before, Unset):
        json_due_at_before = due_at_before.isoformat()
    params["due_at_before"] = json_due_at_before

    params["ids"] = ids

    params["in_trash"] = in_trash

    params["is_completed"] = is_completed

    params["limit"] = limit

    params["offset"] = offset

    params["parent_id"] = parent_id

    params["priority"] = priority

    params["size"] = size

    json_start_at: Union[Unset, str] = UNSET
    if not isinstance(start_at, Unset):
        json_start_at = start_at.isoformat()
    params["start_at"] = json_start_at

    json_start_at_after: Union[Unset, str] = UNSET
    if not isinstance(start_at_after, Unset):
        json_start_at_after = start_at_after.isoformat()
    params["start_at_after"] = json_start_at_after

    json_start_at_before: Union[Unset, str] = UNSET
    if not isinstance(start_at_before, Unset):
        json_start_at_before = start_at_before.isoformat()
    params["start_at_before"] = json_start_at_before

    params["status"] = status

    params["status_id"] = status_id

    params["tag"] = tag

    params["tag_id"] = tag_id

    params["title"] = title

    params["type"] = type_

    params["type_id"] = type_id

    params["view"] = view

    params["view_id"] = view_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/tasks/list",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PaginatedConciseTaskList]:
    if response.status_code == 200:
        response_200 = PaginatedConciseTaskList.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PaginatedConciseTaskList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    assignee: Union[Unset, str] = UNSET,
    assignee_id: Union[Unset, str] = UNSET,
    dartboard: Union[Unset, str] = UNSET,
    dartboard_id: Union[Unset, str] = UNSET,
    description: Union[Unset, str] = UNSET,
    due_at: Union[Unset, datetime.datetime] = UNSET,
    due_at_after: Union[Unset, datetime.datetime] = UNSET,
    due_at_before: Union[Unset, datetime.datetime] = UNSET,
    ids: Union[Unset, str] = UNSET,
    in_trash: Union[Unset, bool] = UNSET,
    is_completed: Union[Unset, bool] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    parent_id: Union[Unset, str] = UNSET,
    priority: Union[Unset, str] = UNSET,
    size: Union[Unset, int] = UNSET,
    start_at: Union[Unset, datetime.datetime] = UNSET,
    start_at_after: Union[Unset, datetime.datetime] = UNSET,
    start_at_before: Union[Unset, datetime.datetime] = UNSET,
    status: Union[Unset, str] = UNSET,
    status_id: Union[Unset, str] = UNSET,
    tag: Union[Unset, str] = UNSET,
    tag_id: Union[Unset, str] = UNSET,
    title: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,
    type_id: Union[Unset, str] = UNSET,
    view: Union[Unset, str] = UNSET,
    view_id: Union[Unset, str] = UNSET,
) -> Response[PaginatedConciseTaskList]:
    """List tasks with powerful filtering options. Filter by dartboard, status, assignee, tags, priority,
    dates, completion state, view, and more. Supports pagination with limit/offset.

    Args:
        assignee (Union[Unset, str]):
        assignee_id (Union[Unset, str]):
        dartboard (Union[Unset, str]):
        dartboard_id (Union[Unset, str]):
        description (Union[Unset, str]):
        due_at (Union[Unset, datetime.datetime]):
        due_at_after (Union[Unset, datetime.datetime]):
        due_at_before (Union[Unset, datetime.datetime]):
        ids (Union[Unset, str]):
        in_trash (Union[Unset, bool]):
        is_completed (Union[Unset, bool]):
        limit (Union[Unset, int]):
        offset (Union[Unset, int]):
        parent_id (Union[Unset, str]):
        priority (Union[Unset, str]):
        size (Union[Unset, int]):
        start_at (Union[Unset, datetime.datetime]):
        start_at_after (Union[Unset, datetime.datetime]):
        start_at_before (Union[Unset, datetime.datetime]):
        status (Union[Unset, str]):
        status_id (Union[Unset, str]):
        tag (Union[Unset, str]):
        tag_id (Union[Unset, str]):
        title (Union[Unset, str]):
        type_ (Union[Unset, str]):
        type_id (Union[Unset, str]):
        view (Union[Unset, str]):
        view_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedConciseTaskList]
    """

    kwargs = _get_kwargs(
        assignee=assignee,
        assignee_id=assignee_id,
        dartboard=dartboard,
        dartboard_id=dartboard_id,
        description=description,
        due_at=due_at,
        due_at_after=due_at_after,
        due_at_before=due_at_before,
        ids=ids,
        in_trash=in_trash,
        is_completed=is_completed,
        limit=limit,
        offset=offset,
        parent_id=parent_id,
        priority=priority,
        size=size,
        start_at=start_at,
        start_at_after=start_at_after,
        start_at_before=start_at_before,
        status=status,
        status_id=status_id,
        tag=tag,
        tag_id=tag_id,
        title=title,
        type_=type_,
        type_id=type_id,
        view=view,
        view_id=view_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    assignee: Union[Unset, str] = UNSET,
    assignee_id: Union[Unset, str] = UNSET,
    dartboard: Union[Unset, str] = UNSET,
    dartboard_id: Union[Unset, str] = UNSET,
    description: Union[Unset, str] = UNSET,
    due_at: Union[Unset, datetime.datetime] = UNSET,
    due_at_after: Union[Unset, datetime.datetime] = UNSET,
    due_at_before: Union[Unset, datetime.datetime] = UNSET,
    ids: Union[Unset, str] = UNSET,
    in_trash: Union[Unset, bool] = UNSET,
    is_completed: Union[Unset, bool] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    parent_id: Union[Unset, str] = UNSET,
    priority: Union[Unset, str] = UNSET,
    size: Union[Unset, int] = UNSET,
    start_at: Union[Unset, datetime.datetime] = UNSET,
    start_at_after: Union[Unset, datetime.datetime] = UNSET,
    start_at_before: Union[Unset, datetime.datetime] = UNSET,
    status: Union[Unset, str] = UNSET,
    status_id: Union[Unset, str] = UNSET,
    tag: Union[Unset, str] = UNSET,
    tag_id: Union[Unset, str] = UNSET,
    title: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,
    type_id: Union[Unset, str] = UNSET,
    view: Union[Unset, str] = UNSET,
    view_id: Union[Unset, str] = UNSET,
) -> Optional[PaginatedConciseTaskList]:
    """List tasks with powerful filtering options. Filter by dartboard, status, assignee, tags, priority,
    dates, completion state, view, and more. Supports pagination with limit/offset.

    Args:
        assignee (Union[Unset, str]):
        assignee_id (Union[Unset, str]):
        dartboard (Union[Unset, str]):
        dartboard_id (Union[Unset, str]):
        description (Union[Unset, str]):
        due_at (Union[Unset, datetime.datetime]):
        due_at_after (Union[Unset, datetime.datetime]):
        due_at_before (Union[Unset, datetime.datetime]):
        ids (Union[Unset, str]):
        in_trash (Union[Unset, bool]):
        is_completed (Union[Unset, bool]):
        limit (Union[Unset, int]):
        offset (Union[Unset, int]):
        parent_id (Union[Unset, str]):
        priority (Union[Unset, str]):
        size (Union[Unset, int]):
        start_at (Union[Unset, datetime.datetime]):
        start_at_after (Union[Unset, datetime.datetime]):
        start_at_before (Union[Unset, datetime.datetime]):
        status (Union[Unset, str]):
        status_id (Union[Unset, str]):
        tag (Union[Unset, str]):
        tag_id (Union[Unset, str]):
        title (Union[Unset, str]):
        type_ (Union[Unset, str]):
        type_id (Union[Unset, str]):
        view (Union[Unset, str]):
        view_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedConciseTaskList
    """

    return sync_detailed(
        client=client,
        assignee=assignee,
        assignee_id=assignee_id,
        dartboard=dartboard,
        dartboard_id=dartboard_id,
        description=description,
        due_at=due_at,
        due_at_after=due_at_after,
        due_at_before=due_at_before,
        ids=ids,
        in_trash=in_trash,
        is_completed=is_completed,
        limit=limit,
        offset=offset,
        parent_id=parent_id,
        priority=priority,
        size=size,
        start_at=start_at,
        start_at_after=start_at_after,
        start_at_before=start_at_before,
        status=status,
        status_id=status_id,
        tag=tag,
        tag_id=tag_id,
        title=title,
        type_=type_,
        type_id=type_id,
        view=view,
        view_id=view_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    assignee: Union[Unset, str] = UNSET,
    assignee_id: Union[Unset, str] = UNSET,
    dartboard: Union[Unset, str] = UNSET,
    dartboard_id: Union[Unset, str] = UNSET,
    description: Union[Unset, str] = UNSET,
    due_at: Union[Unset, datetime.datetime] = UNSET,
    due_at_after: Union[Unset, datetime.datetime] = UNSET,
    due_at_before: Union[Unset, datetime.datetime] = UNSET,
    ids: Union[Unset, str] = UNSET,
    in_trash: Union[Unset, bool] = UNSET,
    is_completed: Union[Unset, bool] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    parent_id: Union[Unset, str] = UNSET,
    priority: Union[Unset, str] = UNSET,
    size: Union[Unset, int] = UNSET,
    start_at: Union[Unset, datetime.datetime] = UNSET,
    start_at_after: Union[Unset, datetime.datetime] = UNSET,
    start_at_before: Union[Unset, datetime.datetime] = UNSET,
    status: Union[Unset, str] = UNSET,
    status_id: Union[Unset, str] = UNSET,
    tag: Union[Unset, str] = UNSET,
    tag_id: Union[Unset, str] = UNSET,
    title: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,
    type_id: Union[Unset, str] = UNSET,
    view: Union[Unset, str] = UNSET,
    view_id: Union[Unset, str] = UNSET,
) -> Response[PaginatedConciseTaskList]:
    """List tasks with powerful filtering options. Filter by dartboard, status, assignee, tags, priority,
    dates, completion state, view, and more. Supports pagination with limit/offset.

    Args:
        assignee (Union[Unset, str]):
        assignee_id (Union[Unset, str]):
        dartboard (Union[Unset, str]):
        dartboard_id (Union[Unset, str]):
        description (Union[Unset, str]):
        due_at (Union[Unset, datetime.datetime]):
        due_at_after (Union[Unset, datetime.datetime]):
        due_at_before (Union[Unset, datetime.datetime]):
        ids (Union[Unset, str]):
        in_trash (Union[Unset, bool]):
        is_completed (Union[Unset, bool]):
        limit (Union[Unset, int]):
        offset (Union[Unset, int]):
        parent_id (Union[Unset, str]):
        priority (Union[Unset, str]):
        size (Union[Unset, int]):
        start_at (Union[Unset, datetime.datetime]):
        start_at_after (Union[Unset, datetime.datetime]):
        start_at_before (Union[Unset, datetime.datetime]):
        status (Union[Unset, str]):
        status_id (Union[Unset, str]):
        tag (Union[Unset, str]):
        tag_id (Union[Unset, str]):
        title (Union[Unset, str]):
        type_ (Union[Unset, str]):
        type_id (Union[Unset, str]):
        view (Union[Unset, str]):
        view_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedConciseTaskList]
    """

    kwargs = _get_kwargs(
        assignee=assignee,
        assignee_id=assignee_id,
        dartboard=dartboard,
        dartboard_id=dartboard_id,
        description=description,
        due_at=due_at,
        due_at_after=due_at_after,
        due_at_before=due_at_before,
        ids=ids,
        in_trash=in_trash,
        is_completed=is_completed,
        limit=limit,
        offset=offset,
        parent_id=parent_id,
        priority=priority,
        size=size,
        start_at=start_at,
        start_at_after=start_at_after,
        start_at_before=start_at_before,
        status=status,
        status_id=status_id,
        tag=tag,
        tag_id=tag_id,
        title=title,
        type_=type_,
        type_id=type_id,
        view=view,
        view_id=view_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    assignee: Union[Unset, str] = UNSET,
    assignee_id: Union[Unset, str] = UNSET,
    dartboard: Union[Unset, str] = UNSET,
    dartboard_id: Union[Unset, str] = UNSET,
    description: Union[Unset, str] = UNSET,
    due_at: Union[Unset, datetime.datetime] = UNSET,
    due_at_after: Union[Unset, datetime.datetime] = UNSET,
    due_at_before: Union[Unset, datetime.datetime] = UNSET,
    ids: Union[Unset, str] = UNSET,
    in_trash: Union[Unset, bool] = UNSET,
    is_completed: Union[Unset, bool] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    parent_id: Union[Unset, str] = UNSET,
    priority: Union[Unset, str] = UNSET,
    size: Union[Unset, int] = UNSET,
    start_at: Union[Unset, datetime.datetime] = UNSET,
    start_at_after: Union[Unset, datetime.datetime] = UNSET,
    start_at_before: Union[Unset, datetime.datetime] = UNSET,
    status: Union[Unset, str] = UNSET,
    status_id: Union[Unset, str] = UNSET,
    tag: Union[Unset, str] = UNSET,
    tag_id: Union[Unset, str] = UNSET,
    title: Union[Unset, str] = UNSET,
    type_: Union[Unset, str] = UNSET,
    type_id: Union[Unset, str] = UNSET,
    view: Union[Unset, str] = UNSET,
    view_id: Union[Unset, str] = UNSET,
) -> Optional[PaginatedConciseTaskList]:
    """List tasks with powerful filtering options. Filter by dartboard, status, assignee, tags, priority,
    dates, completion state, view, and more. Supports pagination with limit/offset.

    Args:
        assignee (Union[Unset, str]):
        assignee_id (Union[Unset, str]):
        dartboard (Union[Unset, str]):
        dartboard_id (Union[Unset, str]):
        description (Union[Unset, str]):
        due_at (Union[Unset, datetime.datetime]):
        due_at_after (Union[Unset, datetime.datetime]):
        due_at_before (Union[Unset, datetime.datetime]):
        ids (Union[Unset, str]):
        in_trash (Union[Unset, bool]):
        is_completed (Union[Unset, bool]):
        limit (Union[Unset, int]):
        offset (Union[Unset, int]):
        parent_id (Union[Unset, str]):
        priority (Union[Unset, str]):
        size (Union[Unset, int]):
        start_at (Union[Unset, datetime.datetime]):
        start_at_after (Union[Unset, datetime.datetime]):
        start_at_before (Union[Unset, datetime.datetime]):
        status (Union[Unset, str]):
        status_id (Union[Unset, str]):
        tag (Union[Unset, str]):
        tag_id (Union[Unset, str]):
        title (Union[Unset, str]):
        type_ (Union[Unset, str]):
        type_id (Union[Unset, str]):
        view (Union[Unset, str]):
        view_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedConciseTaskList
    """

    return (
        await asyncio_detailed(
            client=client,
            assignee=assignee,
            assignee_id=assignee_id,
            dartboard=dartboard,
            dartboard_id=dartboard_id,
            description=description,
            due_at=due_at,
            due_at_after=due_at_after,
            due_at_before=due_at_before,
            ids=ids,
            in_trash=in_trash,
            is_completed=is_completed,
            limit=limit,
            offset=offset,
            parent_id=parent_id,
            priority=priority,
            size=size,
            start_at=start_at,
            start_at_after=start_at_after,
            start_at_before=start_at_before,
            status=status,
            status_id=status_id,
            tag=tag,
            tag_id=tag_id,
            title=title,
            type_=type_,
            type_id=type_id,
            view=view,
            view_id=view_id,
        )
    ).parsed
