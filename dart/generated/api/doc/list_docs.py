from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.list_docs_o_item import ListDocsOItem
from ...models.paginated_concise_doc_list import PaginatedConciseDocList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    editor: Union[Unset, str] = UNSET,
    folder: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    in_trash: Union[Unset, bool] = UNSET,
    limit: Union[Unset, int] = UNSET,
    no_defaults: Union[Unset, bool] = False,
    o: Union[Unset, list[ListDocsOItem]] = UNSET,
    offset: Union[Unset, int] = UNSET,
    s: Union[Unset, str] = UNSET,
    text: Union[Unset, str] = UNSET,
    title: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["editor"] = editor

    params["folder"] = folder

    params["folder_id"] = folder_id

    params["ids"] = ids

    params["in_trash"] = in_trash

    params["limit"] = limit

    params["no_defaults"] = no_defaults

    json_o: Union[Unset, list[str]] = UNSET
    if not isinstance(o, Unset):
        json_o = []
        for o_item_data in o:
            o_item = o_item_data.value
            json_o.append(o_item)

    params["o"] = json_o

    params["offset"] = offset

    params["s"] = s

    params["text"] = text

    params["title"] = title

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/docs/list",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PaginatedConciseDocList]:
    if response.status_code == 200:
        response_200 = PaginatedConciseDocList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PaginatedConciseDocList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    editor: Union[Unset, str] = UNSET,
    folder: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    in_trash: Union[Unset, bool] = UNSET,
    limit: Union[Unset, int] = UNSET,
    no_defaults: Union[Unset, bool] = False,
    o: Union[Unset, list[ListDocsOItem]] = UNSET,
    offset: Union[Unset, int] = UNSET,
    s: Union[Unset, str] = UNSET,
    text: Union[Unset, str] = UNSET,
    title: Union[Unset, str] = UNSET,
) -> Response[PaginatedConciseDocList]:
    """List docs with filtering and search capabilities. Filter by folder, title, text content, or use
    full-text search. Sort by creation/update date or title. Supports pagination.

    Args:
        editor (Union[Unset, str]):
        folder (Union[Unset, str]):
        folder_id (Union[Unset, str]):
        ids (Union[Unset, str]):
        in_trash (Union[Unset, bool]):
        limit (Union[Unset, int]):
        no_defaults (Union[Unset, bool]):  Default: False.
        o (Union[Unset, list[ListDocsOItem]]):
        offset (Union[Unset, int]):
        s (Union[Unset, str]):
        text (Union[Unset, str]):
        title (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedConciseDocList]
    """

    kwargs = _get_kwargs(
        editor=editor,
        folder=folder,
        folder_id=folder_id,
        ids=ids,
        in_trash=in_trash,
        limit=limit,
        no_defaults=no_defaults,
        o=o,
        offset=offset,
        s=s,
        text=text,
        title=title,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    editor: Union[Unset, str] = UNSET,
    folder: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    in_trash: Union[Unset, bool] = UNSET,
    limit: Union[Unset, int] = UNSET,
    no_defaults: Union[Unset, bool] = False,
    o: Union[Unset, list[ListDocsOItem]] = UNSET,
    offset: Union[Unset, int] = UNSET,
    s: Union[Unset, str] = UNSET,
    text: Union[Unset, str] = UNSET,
    title: Union[Unset, str] = UNSET,
) -> Optional[PaginatedConciseDocList]:
    """List docs with filtering and search capabilities. Filter by folder, title, text content, or use
    full-text search. Sort by creation/update date or title. Supports pagination.

    Args:
        editor (Union[Unset, str]):
        folder (Union[Unset, str]):
        folder_id (Union[Unset, str]):
        ids (Union[Unset, str]):
        in_trash (Union[Unset, bool]):
        limit (Union[Unset, int]):
        no_defaults (Union[Unset, bool]):  Default: False.
        o (Union[Unset, list[ListDocsOItem]]):
        offset (Union[Unset, int]):
        s (Union[Unset, str]):
        text (Union[Unset, str]):
        title (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedConciseDocList
    """

    return sync_detailed(
        client=client,
        editor=editor,
        folder=folder,
        folder_id=folder_id,
        ids=ids,
        in_trash=in_trash,
        limit=limit,
        no_defaults=no_defaults,
        o=o,
        offset=offset,
        s=s,
        text=text,
        title=title,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    editor: Union[Unset, str] = UNSET,
    folder: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    in_trash: Union[Unset, bool] = UNSET,
    limit: Union[Unset, int] = UNSET,
    no_defaults: Union[Unset, bool] = False,
    o: Union[Unset, list[ListDocsOItem]] = UNSET,
    offset: Union[Unset, int] = UNSET,
    s: Union[Unset, str] = UNSET,
    text: Union[Unset, str] = UNSET,
    title: Union[Unset, str] = UNSET,
) -> Response[PaginatedConciseDocList]:
    """List docs with filtering and search capabilities. Filter by folder, title, text content, or use
    full-text search. Sort by creation/update date or title. Supports pagination.

    Args:
        editor (Union[Unset, str]):
        folder (Union[Unset, str]):
        folder_id (Union[Unset, str]):
        ids (Union[Unset, str]):
        in_trash (Union[Unset, bool]):
        limit (Union[Unset, int]):
        no_defaults (Union[Unset, bool]):  Default: False.
        o (Union[Unset, list[ListDocsOItem]]):
        offset (Union[Unset, int]):
        s (Union[Unset, str]):
        text (Union[Unset, str]):
        title (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedConciseDocList]
    """

    kwargs = _get_kwargs(
        editor=editor,
        folder=folder,
        folder_id=folder_id,
        ids=ids,
        in_trash=in_trash,
        limit=limit,
        no_defaults=no_defaults,
        o=o,
        offset=offset,
        s=s,
        text=text,
        title=title,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    editor: Union[Unset, str] = UNSET,
    folder: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    in_trash: Union[Unset, bool] = UNSET,
    limit: Union[Unset, int] = UNSET,
    no_defaults: Union[Unset, bool] = False,
    o: Union[Unset, list[ListDocsOItem]] = UNSET,
    offset: Union[Unset, int] = UNSET,
    s: Union[Unset, str] = UNSET,
    text: Union[Unset, str] = UNSET,
    title: Union[Unset, str] = UNSET,
) -> Optional[PaginatedConciseDocList]:
    """List docs with filtering and search capabilities. Filter by folder, title, text content, or use
    full-text search. Sort by creation/update date or title. Supports pagination.

    Args:
        editor (Union[Unset, str]):
        folder (Union[Unset, str]):
        folder_id (Union[Unset, str]):
        ids (Union[Unset, str]):
        in_trash (Union[Unset, bool]):
        limit (Union[Unset, int]):
        no_defaults (Union[Unset, bool]):  Default: False.
        o (Union[Unset, list[ListDocsOItem]]):
        offset (Union[Unset, int]):
        s (Union[Unset, str]):
        text (Union[Unset, str]):
        title (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedConciseDocList
    """

    return (
        await asyncio_detailed(
            client=client,
            editor=editor,
            folder=folder,
            folder_id=folder_id,
            ids=ids,
            in_trash=in_trash,
            limit=limit,
            no_defaults=no_defaults,
            o=o,
            offset=offset,
            s=s,
            text=text,
            title=title,
        )
    ).parsed
