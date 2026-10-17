import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.list_tasks_o_item import ListTasksOItem
from ...models.paginated_concise_task_list import PaginatedConciseTaskList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    assignee: str | Unset = UNSET,
    assignee_id: str | Unset = UNSET,
    completed_at: datetime.datetime | Unset = UNSET,
    completed_at_after: datetime.datetime | Unset = UNSET,
    completed_at_before: datetime.datetime | Unset = UNSET,
    created_at: datetime.datetime | Unset = UNSET,
    created_at_after: datetime.datetime | Unset = UNSET,
    created_at_before: datetime.datetime | Unset = UNSET,
    created_by: str | Unset = UNSET,
    created_by_id: str | Unset = UNSET,
    dartboard: str | Unset = UNSET,
    dartboard_id: str | Unset = UNSET,
    description: str | Unset = UNSET,
    due_at: str | Unset = UNSET,
    due_at_after: str | Unset = UNSET,
    due_at_before: str | Unset = UNSET,
    ids: str | Unset = UNSET,
    in_trash: bool | Unset = UNSET,
    is_completed: bool | Unset = UNSET,
    limit: int | Unset = UNSET,
    no_defaults: bool | Unset = True,
    o: list[ListTasksOItem] | Unset = UNSET,
    offset: int | Unset = UNSET,
    parent_id: str | Unset = UNSET,
    priority: str | Unset = UNSET,
    reviewer: str | Unset = UNSET,
    reviewer_id: str | Unset = UNSET,
    size: int | Unset = UNSET,
    start_at: str | Unset = UNSET,
    start_at_after: str | Unset = UNSET,
    start_at_before: str | Unset = UNSET,
    status: str | Unset = UNSET,
    status_id: str | Unset = UNSET,
    tag: str | Unset = UNSET,
    tag_id: str | Unset = UNSET,
    title: str | Unset = UNSET,
    type_: str | Unset = UNSET,
    type_id: str | Unset = UNSET,
    updated_at: datetime.datetime | Unset = UNSET,
    updated_at_after: datetime.datetime | Unset = UNSET,
    updated_at_before: datetime.datetime | Unset = UNSET,
    updated_by: str | Unset = UNSET,
    updated_by_id: str | Unset = UNSET,
    view: str | Unset = UNSET,
    view_id: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["assignee"] = assignee

    params["assignee_id"] = assignee_id

    json_completed_at: str | Unset = UNSET
    if not isinstance(completed_at, Unset):
        json_completed_at = completed_at.isoformat()
    params["completed_at"] = json_completed_at

    json_completed_at_after: str | Unset = UNSET
    if not isinstance(completed_at_after, Unset):
        json_completed_at_after = completed_at_after.isoformat()
    params["completed_at_after"] = json_completed_at_after

    json_completed_at_before: str | Unset = UNSET
    if not isinstance(completed_at_before, Unset):
        json_completed_at_before = completed_at_before.isoformat()
    params["completed_at_before"] = json_completed_at_before

    json_created_at: str | Unset = UNSET
    if not isinstance(created_at, Unset):
        json_created_at = created_at.isoformat()
    params["created_at"] = json_created_at

    json_created_at_after: str | Unset = UNSET
    if not isinstance(created_at_after, Unset):
        json_created_at_after = created_at_after.isoformat()
    params["created_at_after"] = json_created_at_after

    json_created_at_before: str | Unset = UNSET
    if not isinstance(created_at_before, Unset):
        json_created_at_before = created_at_before.isoformat()
    params["created_at_before"] = json_created_at_before

    params["created_by"] = created_by

    params["created_by_id"] = created_by_id

    params["dartboard"] = dartboard

    params["dartboard_id"] = dartboard_id

    params["description"] = description

    params["due_at"] = due_at

    params["due_at_after"] = due_at_after

    params["due_at_before"] = due_at_before

    params["ids"] = ids

    params["in_trash"] = in_trash

    params["is_completed"] = is_completed

    params["limit"] = limit

    params["no_defaults"] = no_defaults

    json_o: list[str] | Unset = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["offset"] = offset

    params["parent_id"] = parent_id

    params["priority"] = priority

    params["reviewer"] = reviewer

    params["reviewer_id"] = reviewer_id

    params["size"] = size

    params["start_at"] = start_at

    params["start_at_after"] = start_at_after

    params["start_at_before"] = start_at_before

    params["status"] = status

    params["status_id"] = status_id

    params["tag"] = tag

    params["tag_id"] = tag_id

    params["title"] = title

    params["type"] = type_

    params["type_id"] = type_id

    json_updated_at: str | Unset = UNSET
    if not isinstance(updated_at, Unset):
        json_updated_at = updated_at.isoformat()
    params["updated_at"] = json_updated_at

    json_updated_at_after: str | Unset = UNSET
    if not isinstance(updated_at_after, Unset):
        json_updated_at_after = updated_at_after.isoformat()
    params["updated_at_after"] = json_updated_at_after

    json_updated_at_before: str | Unset = UNSET
    if not isinstance(updated_at_before, Unset):
        json_updated_at_before = updated_at_before.isoformat()
    params["updated_at_before"] = json_updated_at_before

    params["updated_by"] = updated_by

    params["updated_by_id"] = updated_by_id

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
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PaginatedConciseTaskList | None:
    if response.status_code == 200:
        response_200 = PaginatedConciseTaskList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedConciseTaskList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    assignee: str | Unset = UNSET,
    assignee_id: str | Unset = UNSET,
    completed_at: datetime.datetime | Unset = UNSET,
    completed_at_after: datetime.datetime | Unset = UNSET,
    completed_at_before: datetime.datetime | Unset = UNSET,
    created_at: datetime.datetime | Unset = UNSET,
    created_at_after: datetime.datetime | Unset = UNSET,
    created_at_before: datetime.datetime | Unset = UNSET,
    created_by: str | Unset = UNSET,
    created_by_id: str | Unset = UNSET,
    dartboard: str | Unset = UNSET,
    dartboard_id: str | Unset = UNSET,
    description: str | Unset = UNSET,
    due_at: str | Unset = UNSET,
    due_at_after: str | Unset = UNSET,
    due_at_before: str | Unset = UNSET,
    ids: str | Unset = UNSET,
    in_trash: bool | Unset = UNSET,
    is_completed: bool | Unset = UNSET,
    limit: int | Unset = UNSET,
    no_defaults: bool | Unset = True,
    o: list[ListTasksOItem] | Unset = UNSET,
    offset: int | Unset = UNSET,
    parent_id: str | Unset = UNSET,
    priority: str | Unset = UNSET,
    reviewer: str | Unset = UNSET,
    reviewer_id: str | Unset = UNSET,
    size: int | Unset = UNSET,
    start_at: str | Unset = UNSET,
    start_at_after: str | Unset = UNSET,
    start_at_before: str | Unset = UNSET,
    status: str | Unset = UNSET,
    status_id: str | Unset = UNSET,
    tag: str | Unset = UNSET,
    tag_id: str | Unset = UNSET,
    title: str | Unset = UNSET,
    type_: str | Unset = UNSET,
    type_id: str | Unset = UNSET,
    updated_at: datetime.datetime | Unset = UNSET,
    updated_at_after: datetime.datetime | Unset = UNSET,
    updated_at_before: datetime.datetime | Unset = UNSET,
    updated_by: str | Unset = UNSET,
    updated_by_id: str | Unset = UNSET,
    view: str | Unset = UNSET,
    view_id: str | Unset = UNSET,
) -> Response[PaginatedConciseTaskList]:
    """List tasks with powerful filtering options. Filter by dartboard, status, assignee, tags, priority,
    dates, completion state, view, and more. Supports pagination with limit/offset.

    Args:
        assignee (str | Unset):
        assignee_id (str | Unset):
        completed_at (datetime.datetime | Unset):
        completed_at_after (datetime.datetime | Unset):
        completed_at_before (datetime.datetime | Unset):
        created_at (datetime.datetime | Unset):
        created_at_after (datetime.datetime | Unset):
        created_at_before (datetime.datetime | Unset):
        created_by (str | Unset):
        created_by_id (str | Unset):
        dartboard (str | Unset):
        dartboard_id (str | Unset):
        description (str | Unset):
        due_at (str | Unset):
        due_at_after (str | Unset):
        due_at_before (str | Unset):
        ids (str | Unset):
        in_trash (bool | Unset):
        is_completed (bool | Unset):
        limit (int | Unset):
        no_defaults (bool | Unset):  Default: True.
        o (list[ListTasksOItem] | Unset):
        offset (int | Unset):
        parent_id (str | Unset):
        priority (str | Unset):
        reviewer (str | Unset):
        reviewer_id (str | Unset):
        size (int | Unset):
        start_at (str | Unset):
        start_at_after (str | Unset):
        start_at_before (str | Unset):
        status (str | Unset):
        status_id (str | Unset):
        tag (str | Unset):
        tag_id (str | Unset):
        title (str | Unset):
        type_ (str | Unset):
        type_id (str | Unset):
        updated_at (datetime.datetime | Unset):
        updated_at_after (datetime.datetime | Unset):
        updated_at_before (datetime.datetime | Unset):
        updated_by (str | Unset):
        updated_by_id (str | Unset):
        view (str | Unset):
        view_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedConciseTaskList]
    """

    kwargs = _get_kwargs(
        assignee=assignee,
        assignee_id=assignee_id,
        completed_at=completed_at,
        completed_at_after=completed_at_after,
        completed_at_before=completed_at_before,
        created_at=created_at,
        created_at_after=created_at_after,
        created_at_before=created_at_before,
        created_by=created_by,
        created_by_id=created_by_id,
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
        no_defaults=no_defaults,
        o=o,
        offset=offset,
        parent_id=parent_id,
        priority=priority,
        reviewer=reviewer,
        reviewer_id=reviewer_id,
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
        updated_at=updated_at,
        updated_at_after=updated_at_after,
        updated_at_before=updated_at_before,
        updated_by=updated_by,
        updated_by_id=updated_by_id,
        view=view,
        view_id=view_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    assignee: str | Unset = UNSET,
    assignee_id: str | Unset = UNSET,
    completed_at: datetime.datetime | Unset = UNSET,
    completed_at_after: datetime.datetime | Unset = UNSET,
    completed_at_before: datetime.datetime | Unset = UNSET,
    created_at: datetime.datetime | Unset = UNSET,
    created_at_after: datetime.datetime | Unset = UNSET,
    created_at_before: datetime.datetime | Unset = UNSET,
    created_by: str | Unset = UNSET,
    created_by_id: str | Unset = UNSET,
    dartboard: str | Unset = UNSET,
    dartboard_id: str | Unset = UNSET,
    description: str | Unset = UNSET,
    due_at: str | Unset = UNSET,
    due_at_after: str | Unset = UNSET,
    due_at_before: str | Unset = UNSET,
    ids: str | Unset = UNSET,
    in_trash: bool | Unset = UNSET,
    is_completed: bool | Unset = UNSET,
    limit: int | Unset = UNSET,
    no_defaults: bool | Unset = True,
    o: list[ListTasksOItem] | Unset = UNSET,
    offset: int | Unset = UNSET,
    parent_id: str | Unset = UNSET,
    priority: str | Unset = UNSET,
    reviewer: str | Unset = UNSET,
    reviewer_id: str | Unset = UNSET,
    size: int | Unset = UNSET,
    start_at: str | Unset = UNSET,
    start_at_after: str | Unset = UNSET,
    start_at_before: str | Unset = UNSET,
    status: str | Unset = UNSET,
    status_id: str | Unset = UNSET,
    tag: str | Unset = UNSET,
    tag_id: str | Unset = UNSET,
    title: str | Unset = UNSET,
    type_: str | Unset = UNSET,
    type_id: str | Unset = UNSET,
    updated_at: datetime.datetime | Unset = UNSET,
    updated_at_after: datetime.datetime | Unset = UNSET,
    updated_at_before: datetime.datetime | Unset = UNSET,
    updated_by: str | Unset = UNSET,
    updated_by_id: str | Unset = UNSET,
    view: str | Unset = UNSET,
    view_id: str | Unset = UNSET,
) -> PaginatedConciseTaskList | None:
    """List tasks with powerful filtering options. Filter by dartboard, status, assignee, tags, priority,
    dates, completion state, view, and more. Supports pagination with limit/offset.

    Args:
        assignee (str | Unset):
        assignee_id (str | Unset):
        completed_at (datetime.datetime | Unset):
        completed_at_after (datetime.datetime | Unset):
        completed_at_before (datetime.datetime | Unset):
        created_at (datetime.datetime | Unset):
        created_at_after (datetime.datetime | Unset):
        created_at_before (datetime.datetime | Unset):
        created_by (str | Unset):
        created_by_id (str | Unset):
        dartboard (str | Unset):
        dartboard_id (str | Unset):
        description (str | Unset):
        due_at (str | Unset):
        due_at_after (str | Unset):
        due_at_before (str | Unset):
        ids (str | Unset):
        in_trash (bool | Unset):
        is_completed (bool | Unset):
        limit (int | Unset):
        no_defaults (bool | Unset):  Default: True.
        o (list[ListTasksOItem] | Unset):
        offset (int | Unset):
        parent_id (str | Unset):
        priority (str | Unset):
        reviewer (str | Unset):
        reviewer_id (str | Unset):
        size (int | Unset):
        start_at (str | Unset):
        start_at_after (str | Unset):
        start_at_before (str | Unset):
        status (str | Unset):
        status_id (str | Unset):
        tag (str | Unset):
        tag_id (str | Unset):
        title (str | Unset):
        type_ (str | Unset):
        type_id (str | Unset):
        updated_at (datetime.datetime | Unset):
        updated_at_after (datetime.datetime | Unset):
        updated_at_before (datetime.datetime | Unset):
        updated_by (str | Unset):
        updated_by_id (str | Unset):
        view (str | Unset):
        view_id (str | Unset):

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
        completed_at=completed_at,
        completed_at_after=completed_at_after,
        completed_at_before=completed_at_before,
        created_at=created_at,
        created_at_after=created_at_after,
        created_at_before=created_at_before,
        created_by=created_by,
        created_by_id=created_by_id,
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
        no_defaults=no_defaults,
        o=o,
        offset=offset,
        parent_id=parent_id,
        priority=priority,
        reviewer=reviewer,
        reviewer_id=reviewer_id,
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
        updated_at=updated_at,
        updated_at_after=updated_at_after,
        updated_at_before=updated_at_before,
        updated_by=updated_by,
        updated_by_id=updated_by_id,
        view=view,
        view_id=view_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    assignee: str | Unset = UNSET,
    assignee_id: str | Unset = UNSET,
    completed_at: datetime.datetime | Unset = UNSET,
    completed_at_after: datetime.datetime | Unset = UNSET,
    completed_at_before: datetime.datetime | Unset = UNSET,
    created_at: datetime.datetime | Unset = UNSET,
    created_at_after: datetime.datetime | Unset = UNSET,
    created_at_before: datetime.datetime | Unset = UNSET,
    created_by: str | Unset = UNSET,
    created_by_id: str | Unset = UNSET,
    dartboard: str | Unset = UNSET,
    dartboard_id: str | Unset = UNSET,
    description: str | Unset = UNSET,
    due_at: str | Unset = UNSET,
    due_at_after: str | Unset = UNSET,
    due_at_before: str | Unset = UNSET,
    ids: str | Unset = UNSET,
    in_trash: bool | Unset = UNSET,
    is_completed: bool | Unset = UNSET,
    limit: int | Unset = UNSET,
    no_defaults: bool | Unset = True,
    o: list[ListTasksOItem] | Unset = UNSET,
    offset: int | Unset = UNSET,
    parent_id: str | Unset = UNSET,
    priority: str | Unset = UNSET,
    reviewer: str | Unset = UNSET,
    reviewer_id: str | Unset = UNSET,
    size: int | Unset = UNSET,
    start_at: str | Unset = UNSET,
    start_at_after: str | Unset = UNSET,
    start_at_before: str | Unset = UNSET,
    status: str | Unset = UNSET,
    status_id: str | Unset = UNSET,
    tag: str | Unset = UNSET,
    tag_id: str | Unset = UNSET,
    title: str | Unset = UNSET,
    type_: str | Unset = UNSET,
    type_id: str | Unset = UNSET,
    updated_at: datetime.datetime | Unset = UNSET,
    updated_at_after: datetime.datetime | Unset = UNSET,
    updated_at_before: datetime.datetime | Unset = UNSET,
    updated_by: str | Unset = UNSET,
    updated_by_id: str | Unset = UNSET,
    view: str | Unset = UNSET,
    view_id: str | Unset = UNSET,
) -> Response[PaginatedConciseTaskList]:
    """List tasks with powerful filtering options. Filter by dartboard, status, assignee, tags, priority,
    dates, completion state, view, and more. Supports pagination with limit/offset.

    Args:
        assignee (str | Unset):
        assignee_id (str | Unset):
        completed_at (datetime.datetime | Unset):
        completed_at_after (datetime.datetime | Unset):
        completed_at_before (datetime.datetime | Unset):
        created_at (datetime.datetime | Unset):
        created_at_after (datetime.datetime | Unset):
        created_at_before (datetime.datetime | Unset):
        created_by (str | Unset):
        created_by_id (str | Unset):
        dartboard (str | Unset):
        dartboard_id (str | Unset):
        description (str | Unset):
        due_at (str | Unset):
        due_at_after (str | Unset):
        due_at_before (str | Unset):
        ids (str | Unset):
        in_trash (bool | Unset):
        is_completed (bool | Unset):
        limit (int | Unset):
        no_defaults (bool | Unset):  Default: True.
        o (list[ListTasksOItem] | Unset):
        offset (int | Unset):
        parent_id (str | Unset):
        priority (str | Unset):
        reviewer (str | Unset):
        reviewer_id (str | Unset):
        size (int | Unset):
        start_at (str | Unset):
        start_at_after (str | Unset):
        start_at_before (str | Unset):
        status (str | Unset):
        status_id (str | Unset):
        tag (str | Unset):
        tag_id (str | Unset):
        title (str | Unset):
        type_ (str | Unset):
        type_id (str | Unset):
        updated_at (datetime.datetime | Unset):
        updated_at_after (datetime.datetime | Unset):
        updated_at_before (datetime.datetime | Unset):
        updated_by (str | Unset):
        updated_by_id (str | Unset):
        view (str | Unset):
        view_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedConciseTaskList]
    """

    kwargs = _get_kwargs(
        assignee=assignee,
        assignee_id=assignee_id,
        completed_at=completed_at,
        completed_at_after=completed_at_after,
        completed_at_before=completed_at_before,
        created_at=created_at,
        created_at_after=created_at_after,
        created_at_before=created_at_before,
        created_by=created_by,
        created_by_id=created_by_id,
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
        no_defaults=no_defaults,
        o=o,
        offset=offset,
        parent_id=parent_id,
        priority=priority,
        reviewer=reviewer,
        reviewer_id=reviewer_id,
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
        updated_at=updated_at,
        updated_at_after=updated_at_after,
        updated_at_before=updated_at_before,
        updated_by=updated_by,
        updated_by_id=updated_by_id,
        view=view,
        view_id=view_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    assignee: str | Unset = UNSET,
    assignee_id: str | Unset = UNSET,
    completed_at: datetime.datetime | Unset = UNSET,
    completed_at_after: datetime.datetime | Unset = UNSET,
    completed_at_before: datetime.datetime | Unset = UNSET,
    created_at: datetime.datetime | Unset = UNSET,
    created_at_after: datetime.datetime | Unset = UNSET,
    created_at_before: datetime.datetime | Unset = UNSET,
    created_by: str | Unset = UNSET,
    created_by_id: str | Unset = UNSET,
    dartboard: str | Unset = UNSET,
    dartboard_id: str | Unset = UNSET,
    description: str | Unset = UNSET,
    due_at: str | Unset = UNSET,
    due_at_after: str | Unset = UNSET,
    due_at_before: str | Unset = UNSET,
    ids: str | Unset = UNSET,
    in_trash: bool | Unset = UNSET,
    is_completed: bool | Unset = UNSET,
    limit: int | Unset = UNSET,
    no_defaults: bool | Unset = True,
    o: list[ListTasksOItem] | Unset = UNSET,
    offset: int | Unset = UNSET,
    parent_id: str | Unset = UNSET,
    priority: str | Unset = UNSET,
    reviewer: str | Unset = UNSET,
    reviewer_id: str | Unset = UNSET,
    size: int | Unset = UNSET,
    start_at: str | Unset = UNSET,
    start_at_after: str | Unset = UNSET,
    start_at_before: str | Unset = UNSET,
    status: str | Unset = UNSET,
    status_id: str | Unset = UNSET,
    tag: str | Unset = UNSET,
    tag_id: str | Unset = UNSET,
    title: str | Unset = UNSET,
    type_: str | Unset = UNSET,
    type_id: str | Unset = UNSET,
    updated_at: datetime.datetime | Unset = UNSET,
    updated_at_after: datetime.datetime | Unset = UNSET,
    updated_at_before: datetime.datetime | Unset = UNSET,
    updated_by: str | Unset = UNSET,
    updated_by_id: str | Unset = UNSET,
    view: str | Unset = UNSET,
    view_id: str | Unset = UNSET,
) -> PaginatedConciseTaskList | None:
    """List tasks with powerful filtering options. Filter by dartboard, status, assignee, tags, priority,
    dates, completion state, view, and more. Supports pagination with limit/offset.

    Args:
        assignee (str | Unset):
        assignee_id (str | Unset):
        completed_at (datetime.datetime | Unset):
        completed_at_after (datetime.datetime | Unset):
        completed_at_before (datetime.datetime | Unset):
        created_at (datetime.datetime | Unset):
        created_at_after (datetime.datetime | Unset):
        created_at_before (datetime.datetime | Unset):
        created_by (str | Unset):
        created_by_id (str | Unset):
        dartboard (str | Unset):
        dartboard_id (str | Unset):
        description (str | Unset):
        due_at (str | Unset):
        due_at_after (str | Unset):
        due_at_before (str | Unset):
        ids (str | Unset):
        in_trash (bool | Unset):
        is_completed (bool | Unset):
        limit (int | Unset):
        no_defaults (bool | Unset):  Default: True.
        o (list[ListTasksOItem] | Unset):
        offset (int | Unset):
        parent_id (str | Unset):
        priority (str | Unset):
        reviewer (str | Unset):
        reviewer_id (str | Unset):
        size (int | Unset):
        start_at (str | Unset):
        start_at_after (str | Unset):
        start_at_before (str | Unset):
        status (str | Unset):
        status_id (str | Unset):
        tag (str | Unset):
        tag_id (str | Unset):
        title (str | Unset):
        type_ (str | Unset):
        type_id (str | Unset):
        updated_at (datetime.datetime | Unset):
        updated_at_after (datetime.datetime | Unset):
        updated_at_before (datetime.datetime | Unset):
        updated_by (str | Unset):
        updated_by_id (str | Unset):
        view (str | Unset):
        view_id (str | Unset):

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
            completed_at=completed_at,
            completed_at_after=completed_at_after,
            completed_at_before=completed_at_before,
            created_at=created_at,
            created_at_after=created_at_after,
            created_at_before=created_at_before,
            created_by=created_by,
            created_by_id=created_by_id,
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
            no_defaults=no_defaults,
            o=o,
            offset=offset,
            parent_id=parent_id,
            priority=priority,
            reviewer=reviewer,
            reviewer_id=reviewer_id,
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
            updated_at=updated_at,
            updated_at_after=updated_at_after,
            updated_at_before=updated_at_before,
            updated_by=updated_by,
            updated_by_id=updated_by_id,
            view=view,
            view_id=view_id,
        )
    ).parsed
