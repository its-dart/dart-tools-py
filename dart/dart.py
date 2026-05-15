#!/usr/bin/env uv run python3
# -*- coding: utf-8 -*-

"""A CLI to interact with the Dart web app."""

# Required for type hinting compatibility when using Python 3.9
from __future__ import annotations

import json
import os
import random
import re
import signal
import string
import sys
import threading
import time
from argparse import ArgumentParser
from collections import defaultdict
from datetime import timezone
from functools import wraps
from importlib.metadata import version
from typing import Callable, NoReturn, TypeVar, Union
from webbrowser import open_new_tab

import dateparser
import httpx
import platformdirs
from pick import pick

from .agent import AgentAuthError
from .agent import connect_agent as _connect_local_agent
from .exception import DartException
from .generated import Client, api
from .generated.models import (
    Agent,
    AgentCreate,
    AgentExecutionMode,
    AgentForwarding,
    AgentInstructions,
    AgentLocal,
    AgentUpdate,
    AgentWorkflow,
    Comment,
    CommentCreate,
    ConciseTask,
    Doc,
    DocCreate,
    DocUpdate,
    EventKind,
    LocalAgent,
    PaginatedCommentList,
    PaginatedConciseDocList,
    PaginatedConciseTaskList,
    Priority,
    Task,
    TaskCreate,
    TaskUpdate,
    UserSpaceConfiguration,
    WrappedAgent,
    WrappedAgentCreate,
    WrappedAgentUpdate,
    WrappedComment,
    WrappedCommentCreate,
    WrappedDoc,
    WrappedDocCreate,
    WrappedDocUpdate,
    WrappedTask,
    WrappedTaskCreate,
    WrappedTaskUpdate,
)
from .generated.types import UNSET, Response, Unset
from .server import DEFAULT_PORT as _SERVER_DEFAULT_PORT
from .server import run_server

_APP = "dart-tools"
_PROG = "dart"

_PROD_HOST = "https://app.dartai.com"
_STAG_HOST = "https://stag.dartai.com"
_DEV_HOST = "http://localhost:5100"
_HOST_MAP = {"prod": _PROD_HOST, "stag": _STAG_HOST, "dev": _DEV_HOST, "local": _DEV_HOST}
_REVERSE_HOST_MAP = {v: k for k, v in _HOST_MAP.items()}

# Service commands
_VERSION_CMD = "--version"
_GET_HOST_CMD = "host-get"
_SET_HOST_CMD = "host-set"
_LOGIN_CMD = "login"
# Agent commands
_CREATE_AGENT_CMD = "agent-create"
_UPDATE_AGENT_CMD = "agent-update"
_DELETE_AGENT_CMD = "agent-delete"
_CONNECT_AGENT_CMD = "agent-connect"
# Task commands
_CREATE_TASK_CMD = "task-create"
_UPDATE_TASK_CMD = "task-update"
_DELETE_TASK_CMD = "task-delete"
_BEGIN_TASK_CMD = "task-begin"
# Doc commands
_CREATE_DOC_CMD = "doc-create"
_UPDATE_DOC_CMD = "doc-update"
_DELETE_DOC_CMD = "doc-delete"
# Comment commands
_CREATE_COMMENT_CMD = "comment-create"
# Other commands
_SERVER_START_CMD = "server-start"

_PROFILE_SETTINGS_URL_FRAG = "/?settings=account"
_ROOT_PUBLIC_API_URL_FRAG = "/api/v0/public"

_DEFAULT_BEGIN_STATUS = "Doing"

_AUTH_TOKEN_ENVVAR_KEY = "DART_TOKEN"
_HOST_ENVVAR_KEY = "DART_HOST"
_CONFIG_FPATH = platformdirs.user_config_path(_APP)
_AUTH_FAILURE_STATUS_CODES = (401, 403)
_CLIENT_ID_KEY = "clientId"
_HOST_KEY = "host"
_HOSTS_KEY = "hosts"
_AUTH_TOKEN_KEY = "authToken"

_VERSION_CHECK_KEY = "versionCheck"
_VERSION_CHECK_LATEST_KEY = "latest"
_VERSION_CHECK_AT_KEY = "checkedAt"
_VERSION_CHECK_TTL_S = 24 * 60 * 60
_VERSION_CHECK_JOIN_TIMEOUT_S = 0.5
_PYPI_VERSION_URL = "https://pypi.org/pypi/dart-tools/json"

_ID_CHARS = string.ascii_lowercase + string.ascii_uppercase + string.digits
_NON_ALPHANUM_RE = re.compile(r"[^a-zA-Z0-9-]+")
_REPEATED_DASH_RE = re.compile(r"-{2,}")
_PRIORITY_MAP: dict[int, str] = {
    0: Priority.CRITICAL,
    1: Priority.HIGH,
    2: Priority.MEDIUM,
    3: Priority.LOW,
}
_SIZES = {1, 2, 3, 5, 8}

_VERSION = version(_APP)
_AUTH_TOKEN_ENVVAR = os.environ.get(_AUTH_TOKEN_ENVVAR_KEY)
_HOST_ENVVAR = os.environ.get(_HOST_ENVVAR_KEY)
_DEFAULT_HOST = _HOST_ENVVAR or _PROD_HOST


def _get_help_text(fn: Callable) -> str:
    if fn.__doc__ is None:
        raise ValueError(f"Function {fn.__name__} has no docstring")
    return fn.__doc__.split("\n")[0].lower()


_HELP_TEXT_TO_COMMAND = {
    _CREATE_AGENT_CMD: _get_help_text(api.create_agent.sync_detailed),
    _UPDATE_AGENT_CMD: _get_help_text(api.update_agent.sync_detailed),
    _DELETE_AGENT_CMD: _get_help_text(api.delete_agent.sync_detailed),
    _CREATE_TASK_CMD: _get_help_text(api.create_task.sync_detailed),
    _UPDATE_TASK_CMD: _get_help_text(api.update_task.sync_detailed),
    _DELETE_TASK_CMD: _get_help_text(api.delete_task.sync_detailed),
    _CREATE_DOC_CMD: _get_help_text(api.create_doc.sync_detailed),
    _UPDATE_DOC_CMD: _get_help_text(api.update_doc.sync_detailed),
    _DELETE_DOC_CMD: _get_help_text(api.delete_doc.sync_detailed),
    _CREATE_COMMENT_CMD: _get_help_text(api.add_task_comment.sync_detailed),
}

_is_cli = False


# TODO dedupe these functions with other usages elsewhere
def _make_id() -> str:
    return "".join(random.choices(_ID_CHARS, k=12))


def trim_slug_str(s: str, length: int, max_under: Union[int, None] = None) -> str:
    max_under = max_under if max_under is not None else length // 6
    if len(s) <= length:
        return s
    for i in range(1, max_under + 1):
        if s[length - i] == "-":
            return s[: length - i]
    return s[:length]


def slugify_str(s: str, lower: bool = False, trim_kwargs: Union[dict, None] = None) -> str:
    lowered = s.lower() if lower else s
    formatted = _NON_ALPHANUM_RE.sub("-", lowered.replace("'", ""))
    formatted = _REPEATED_DASH_RE.sub("-", formatted).strip("-")
    return trim_slug_str(formatted, **trim_kwargs) if trim_kwargs is not None else formatted


def _suppress_exception(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:  # pylint: disable=broad-except
            return None

    return wrapper


def _dart_exit(message: str) -> NoReturn:
    if _is_cli:
        sys.exit(message)
    raise DartException(message)


def _exit_gracefully(_signal_received, _frame) -> None:
    _dart_exit("Quitting.")


def _log(s: str) -> None:
    if not _is_cli:
        return
    print(s)


def _get_required_text(prompt: str) -> str:
    while True:
        result = input(prompt).strip()
        if result:
            return result
        _log("Please enter a value.")


T = TypeVar("T")


def _get_response_parsed(response: Response[T], not_found_message="Not found.") -> T:
    if response.parsed is not None:
        return response.parsed
    if response.status_code in _AUTH_FAILURE_STATUS_CODES:
        _auth_failure_exit()
    elif response.status_code == 404:
        _dart_exit(not_found_message)
    try:
        response_content = json.loads(response.content)
        error_message = response_content.get("detail") or " ".join(response_content.get("errors", []))
        _dart_exit(error_message)
    except (json.JSONDecodeError, AttributeError):
        _unknown_failure_exit()


def _handle_request_errors(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except DartException as ex:
            _dart_exit(ex)
        except (httpx.TimeoutException, httpx.RequestError, httpx.ConnectError) as ex:
            _dart_exit(f"Failed to execute API call: {ex}.")

    return wrapper


class _Config:
    def __init__(self):
        self._content = {}
        if os.path.isfile(_CONFIG_FPATH):
            try:
                with open(_CONFIG_FPATH, "r", encoding="UTF-8") as fin:
                    self._content = json.load(fin)
            except OSError:
                pass
        self._content = {
            _CLIENT_ID_KEY: _make_id(),
            _HOST_KEY: _DEFAULT_HOST,
            _HOSTS_KEY: {},
        } | self._content
        self._content[_HOSTS_KEY] = defaultdict(dict, self._content[_HOSTS_KEY])
        self._write()

    def _write(self) -> None:
        try:
            with open(_CONFIG_FPATH, "w+", encoding="UTF-8") as fout:
                json.dump(self._content, fout, indent=2)
        except OSError:
            pass

    @property
    def client_id(self) -> str:
        return self._content[_CLIENT_ID_KEY]

    @property
    def host(self) -> str:
        return self._content[_HOST_KEY]

    @host.setter
    def host(self, v: str) -> None:
        self._content[_HOST_KEY] = v
        self._write()

    def get(self, k: str) -> str | None:
        return self._content[_HOSTS_KEY][self.host].get(k)

    def set(self, k: str, v: str) -> None:
        self._content[_HOSTS_KEY][self.host][k] = v
        self._write()

    def get_cached_latest_version(self) -> str | None:
        cache = self._content.get(_VERSION_CHECK_KEY)
        if not isinstance(cache, dict):
            return None
        checked_at = cache.get(_VERSION_CHECK_AT_KEY, 0)
        if time.time() - checked_at >= _VERSION_CHECK_TTL_S:
            return None
        latest = cache.get(_VERSION_CHECK_LATEST_KEY)
        return latest if isinstance(latest, str) else None

    def set_cached_latest_version(self, latest: str) -> None:
        self._content[_VERSION_CHECK_KEY] = {
            _VERSION_CHECK_LATEST_KEY: latest,
            _VERSION_CHECK_AT_KEY: time.time(),
        }
        self._write()


class Dart:
    def __init__(self, config=None):
        self._config = config or _Config()
        self._init_clients()

    def _init_clients(self) -> None:
        self._public_api = Client(
            base_url=self.get_base_url() + _ROOT_PUBLIC_API_URL_FRAG,
            headers=self.get_headers(),
        )

    def get_base_url(self) -> str:
        return self._config.host

    def get_client_id(self) -> str:
        return self._config.client_id

    def get_auth_token(self) -> Union[str, None]:
        result = self._config.get(_AUTH_TOKEN_KEY)
        if result is not None:
            return result
        return _AUTH_TOKEN_ENVVAR

    def get_headers(self) -> dict[str, str]:
        result = {
            "Origin": self._config.host,
            "client-duid": self.get_client_id(),
        }
        if (auth_token := self.get_auth_token()) is not None:
            result["Authorization"] = f"Bearer {auth_token}"
        return result

    def is_logged_in(self) -> bool:
        self._init_clients()
        try:
            config = api.get_config.sync(client=self._public_api)
            if config is None:
                return False
        except:
            return False
        return True

    @_handle_request_errors
    def get_config(self) -> UserSpaceConfiguration:
        response = api.get_config.sync_detailed(client=self._public_api)
        return _get_response_parsed(response)

    @_handle_request_errors
    def create_agent(self, body: WrappedAgentCreate) -> WrappedAgent:
        response = api.create_agent.sync_detailed(client=self._public_api, body=body)
        return _get_response_parsed(response)

    @_handle_request_errors
    def update_agent(self, id: str, body: WrappedAgentUpdate) -> WrappedAgent:
        response = api.update_agent.sync_detailed(id, client=self._public_api, body=body)
        return _get_response_parsed(response, not_found_message=f"Agent with ID {id} not found.")

    @_handle_request_errors
    def delete_agent(self, id: str) -> WrappedAgent:
        response = api.delete_agent.sync_detailed(id, client=self._public_api)
        return _get_response_parsed(response, not_found_message=f"Agent with ID {id} not found.")

    @_handle_request_errors
    def create_task(self, body: WrappedTaskCreate) -> WrappedTask:
        response = api.create_task.sync_detailed(client=self._public_api, body=body)
        return _get_response_parsed(response)

    @_handle_request_errors
    def retrieve_task(self, id: str) -> WrappedTask:
        response = api.get_task.sync_detailed(id, client=self._public_api)
        return _get_response_parsed(response, not_found_message=f"Task with ID {id} not found.")

    @_handle_request_errors
    def update_task(self, id: str, body: WrappedTaskUpdate) -> WrappedTask:
        response = api.update_task.sync_detailed(id, client=self._public_api, body=body)
        return _get_response_parsed(response, not_found_message=f"Task with ID {id} not found.")

    @_handle_request_errors
    def delete_task(self, id: str) -> WrappedTask:
        response = api.delete_task.sync_detailed(id, client=self._public_api)
        return _get_response_parsed(response, not_found_message=f"Task with ID {id} not found.")

    @_handle_request_errors
    def list_tasks(self, **kwargs) -> PaginatedConciseTaskList:
        response = api.list_tasks.sync_detailed(client=self._public_api, **kwargs)
        return _get_response_parsed(response)

    @_handle_request_errors
    def create_comment(self, body: WrappedCommentCreate) -> WrappedComment:
        response = api.add_task_comment.sync_detailed(client=self._public_api, body=body)
        return _get_response_parsed(response)

    @_handle_request_errors
    def list_comments(self, **kwargs) -> PaginatedCommentList:
        response = api.list_comments.sync_detailed(client=self._public_api, **kwargs)
        return _get_response_parsed(response)

    @_handle_request_errors
    def create_doc(self, body: WrappedDocCreate) -> WrappedDoc:
        response = api.create_doc.sync_detailed(client=self._public_api, body=body)
        return _get_response_parsed(response)

    @_handle_request_errors
    def retrieve_doc(self, id: str) -> WrappedDoc:
        response = api.get_doc.sync_detailed(id, client=self._public_api)
        return _get_response_parsed(response, not_found_message=f"Doc with ID {id} not found.")

    @_handle_request_errors
    def update_doc(self, id: str, body: WrappedDocUpdate) -> WrappedDoc:
        response = api.update_doc.sync_detailed(id, client=self._public_api, body=body)
        return _get_response_parsed(response, not_found_message=f"Doc with ID {id} not found.")

    @_handle_request_errors
    def delete_doc(self, id: str) -> WrappedDoc:
        response = api.delete_doc.sync_detailed(id, client=self._public_api)
        return _get_response_parsed(response, not_found_message=f"Doc with ID {id} not found.")

    @_handle_request_errors
    def list_docs(self, **kwargs) -> PaginatedConciseDocList:
        response = api.list_docs.sync_detailed(client=self._public_api, **kwargs)
        return _get_response_parsed(response)


def make_task_branch_name(email: str, task: ConciseTask | Task) -> str:
    username = slugify_str(email.split("@")[0], lower=True)
    title = slugify_str(task.title, lower=True)
    return trim_slug_str(f"{username}/{task.id}-{title}", length=60)


def get_host() -> str:
    config = _Config()

    host = config.host
    _log(f"Host is {_REVERSE_HOST_MAP.get(host, host)}")
    _log("Done.")
    return host


def set_host(host: str) -> bool:
    config = _Config()

    new_host = _HOST_MAP.get(host, host)
    config.host = new_host

    _log(f"Set host to {new_host}")
    _log("Done.")
    return True


def _auth_failure_exit() -> NoReturn:
    _dart_exit(
        f"Not logged in, run\n\n  {_PROG} {_LOGIN_CMD}\n\nto log in."
        if _is_cli
        else "Not logged in, either run\n\n  dart.login(token)\n\nor save the token into the DART_TOKEN environment variable."
    )


def _unknown_failure_exit() -> NoReturn:
    _dart_exit("Unknown failure, email\n\n  support@dartai.com\n\nfor help.")


def print_version() -> str:
    result = f"dart-tools version {_VERSION}"
    _log(result)
    return result


_pending_version_message: list[str] = []


@_suppress_exception
def _fetch_and_cache_latest_version(config: _Config) -> str | None:
    response = httpx.get(_PYPI_VERSION_URL, timeout=2.0)
    response.raise_for_status()
    latest = response.json()["info"]["version"]
    if isinstance(latest, str):
        config.set_cached_latest_version(latest)
        return latest
    return None


@_suppress_exception
def _check_for_version_update(config: _Config) -> None:
    latest = config.get_cached_latest_version() or _fetch_and_cache_latest_version(config)
    if latest is None or latest == _VERSION:
        return
    if [int(e) for e in latest.split(".")] <= [int(e) for e in _VERSION.split(".")]:
        return
    _pending_version_message.append(
        f"A new version of dart-tools is available. Upgrade from {_VERSION} to {latest} with\n\n  pip install --upgrade dart-tools\n"
    )


def _start_version_check_thread() -> threading.Thread:
    thread = threading.Thread(target=_check_for_version_update, args=(_Config(),), daemon=True)
    thread.start()
    return thread


def _print_pending_version_message(thread: threading.Thread) -> None:
    thread.join(timeout=_VERSION_CHECK_JOIN_TIMEOUT_S)
    if _pending_version_message:
        _log(_pending_version_message[0])


def is_logged_in(should_raise: bool = False) -> bool:
    dart = Dart()
    result = dart.is_logged_in()

    if not result and should_raise:
        _auth_failure_exit()
    _log(f"You are{'' if result else ' not'} logged in")
    return result


def login(token: str | None = None) -> bool:
    config = _Config()
    dart = Dart(config=config)

    if dart.is_logged_in():
        _log("Already logged in.")
        return True

    _log("Log in to Dart")
    if token is None:
        if not _is_cli:
            _dart_exit("Login failed, token is required.")
        _log("Dart is opening in your browser, log in if needed and copy your authentication token from the page")
        open_new_tab(config.host + _PROFILE_SETTINGS_URL_FRAG)
        token = input("Token: ")

    config.set(_AUTH_TOKEN_KEY, token)

    worked = dart.is_logged_in()
    if not worked:
        _dart_exit("Invalid token.")

    _log("Logged in.")
    return True


def begin_task(
    id: str,
    *,
    status_name: str = _DEFAULT_BEGIN_STATUS,
) -> bool:
    dart = Dart()
    config = dart.get_config()
    task = dart.retrieve_task(id).item

    user = config.user

    update_kwargs: dict = {}
    if status_name in config.statuses and task.status != status_name:
        update_kwargs["status"] = status_name

    current_assignees = task.assignees if isinstance(task.assignees, list) else []
    if user.email not in current_assignees:
        update_kwargs["assignees"] = [*current_assignees, user.email]

    if update_kwargs:
        task_update = WrappedTaskUpdate(item=TaskUpdate(task.id, **update_kwargs))
        task = dart.update_task(task.id, task_update).item

    branch_name = make_task_branch_name(user.email, task)

    _log(f"Started work on\n\n  {task.title}\n  {task.html_url}\n  {branch_name}\n")
    return True


def begin_task_interactive(
    *,
    status_name: str = _DEFAULT_BEGIN_STATUS,
    dartboard_title: Union[Unset, str] = UNSET,
) -> bool:
    dart = Dart()
    config = dart.get_config()
    user = config.user
    filtered_tasks = dart.list_tasks(assignee=user.email, is_completed=False, dartboard=dartboard_title).results

    if not filtered_tasks:
        _dart_exit("No active, incomplete tasks found.")

    picked_idx = pick(
        [e.title for e in filtered_tasks],
        "Which of your active, incomplete tasks are you beginning work on?",
        "→",
    )[1]

    begin_task(filtered_tasks[picked_idx].id, status_name=status_name)

    _log("Done.")
    return True


def _normalize_priority(priority_int: Union[int, None, Unset]) -> Union[str, None, Unset]:
    if priority_int in (None, UNSET):
        return priority_int

    if priority_int not in _PRIORITY_MAP:
        _dart_exit(f"Invalid priority {priority_int}. Valid values are {list(_PRIORITY_MAP.keys())}.")

    return _PRIORITY_MAP[priority_int]


def _get_due_at_from_str_arg(due_at_str: Union[str, None, Unset]) -> Union[str, None, Unset]:
    if due_at_str in (None, UNSET):
        return due_at_str

    due_at = dateparser.parse(due_at_str)
    if not due_at:
        _dart_exit(f"Could not parse due date: {due_at_str}.")
    due_at = due_at.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc).isoformat()

    return due_at


def create_agent(
    name: str,
    *,
    execution_mode: Union[AgentExecutionMode, Unset] = UNSET,
    instructions: Union[AgentInstructions, Unset] = UNSET,
    forwarding: Union[AgentForwarding, Unset] = UNSET,
    local: Union[AgentLocal, Unset] = UNSET,
) -> Agent:
    dart = Dart()
    agent_create = WrappedAgentCreate(
        item=AgentCreate(
            name=name,
            execution_mode=execution_mode,
            instructions=instructions,
            forwarding=forwarding,
            local=local,
        )
    )
    agent = dart.create_agent(agent_create).item
    _log(f"Created agent\n\n  {agent.name}\n  ID: {agent.id}\n")
    _log("Done.")
    return agent


def create_agent_interactive(*, execution_mode: AgentExecutionMode | None = None) -> Agent:
    name = _get_required_text("Name: ")
    if execution_mode is None:
        execution_mode = pick(
            list(AgentExecutionMode),
            "Which execution mode should the agent use?",
            "→",
        )[0]

    instructions: Union[AgentInstructions, Unset] = UNSET
    forwarding: Union[AgentForwarding, Unset] = UNSET
    local: Union[AgentLocal, Unset] = UNSET

    if execution_mode == AgentExecutionMode.INSTRUCTIONS:
        instructions = AgentInstructions(markdown=_get_required_text("Instructions: "))
    elif execution_mode == AgentExecutionMode.FORWARDING:
        url = _get_required_text("Forwarding URL: ")
        forwarding = AgentForwarding(
            workflows=[
                AgentWorkflow(
                    _make_id(),
                    EventKind.AGENTSREQUESTED,
                    url,
                )
            ]
        )
    elif execution_mode == AgentExecutionMode.LOCAL:
        local_agent = pick(
            list(LocalAgent),
            "Which local agent should this Dart agent use?",
            "→",
        )[0]
        local = AgentLocal(agent=local_agent)

    return create_agent(
        name,
        execution_mode=execution_mode,
        instructions=instructions,
        forwarding=forwarding,
        local=local,
    )


def update_agent(
    id: str,
    *,
    name: Union[str, Unset] = UNSET,
    execution_mode: Union[AgentExecutionMode, Unset] = UNSET,
    instructions: Union[AgentInstructions, Unset] = UNSET,
    forwarding: Union[AgentForwarding, Unset] = UNSET,
    local: Union[AgentLocal, Unset] = UNSET,
) -> Agent:
    dart = Dart()
    agent_update = WrappedAgentUpdate(
        item=AgentUpdate(
            id=id,
            name=name,
            execution_mode=execution_mode,
            instructions=instructions,
            forwarding=forwarding,
            local=local,
        )
    )
    agent = dart.update_agent(id, agent_update).item
    _log(f"Updated agent\n\n  {agent.name}\n  ID: {agent.id}\n")
    _log("Done.")
    return agent


def delete_agent(id: str) -> Agent:
    dart = Dart()
    agent = dart.delete_agent(id).item

    _log(f"Deleted agent\n\n  {agent.name}\n  ID: {agent.id}\n")
    _log("Done.")
    return agent


def connect_agent(id: str | None = None, *, quiet: bool = False) -> None:
    if id is None:
        id = create_agent_interactive(execution_mode=AgentExecutionMode.LOCAL).id

    dart = Dart()
    try:
        _connect_local_agent(id, base_url=dart.get_base_url(), headers=dart.get_headers(), quiet=quiet)
    except AgentAuthError:
        _auth_failure_exit()


def create_task(
    title: str,
    *,
    dartboard_title: Union[str, Unset] = UNSET,
    status_title: Union[str, Unset] = UNSET,
    assignee_emails: Union[list[str], Unset] = UNSET,
    tag_titles: Union[list[str], Unset] = UNSET,
    priority_int: Union[int, None, Unset] = UNSET,
    size_int: Union[int, None, Unset] = UNSET,
    due_at_str: Union[str, None, Unset] = UNSET,
    should_begin: bool = False,
    begin_status_name: str = _DEFAULT_BEGIN_STATUS,
) -> Task:
    dart = Dart()
    task_create = WrappedTaskCreate(
        item=TaskCreate(
            title,
            dartboard=dartboard_title,
            status=status_title,
            assignees=assignee_emails if assignee_emails is not None else UNSET,
            tags=tag_titles if tag_titles is not None else UNSET,
            priority=_normalize_priority(priority_int),
            size=size_int,
            due_at=_get_due_at_from_str_arg(due_at_str),
        )
    )
    task = dart.create_task(task_create).item
    _log(f"Created task\n\n  {task.title}\n  {task.html_url}\n  ID: {task.id}\n")

    if should_begin:
        begin_task(task.id, status_name=begin_status_name)

    _log("Done.")
    return task


def update_task(
    id: str,
    *,
    title: Union[Unset, str] = UNSET,
    dartboard_title: Union[str, Unset] = UNSET,
    status_title: Union[str, Unset] = UNSET,
    assignee_emails: Union[list[str], Unset] = UNSET,
    tag_titles: Union[list[str], Unset] = UNSET,
    priority_int: Union[int, None, Unset] = UNSET,
    size_int: Union[int, None, Unset] = UNSET,
    due_at_str: Union[str, None, Unset] = UNSET,
) -> Task:
    dart = Dart()
    task_update = WrappedTaskUpdate(
        item=TaskUpdate(
            id,
            title=title,
            dartboard=dartboard_title,
            status=status_title,
            assignees=assignee_emails if assignee_emails is not None else UNSET,
            tags=tag_titles if tag_titles is not None else UNSET,
            priority=_normalize_priority(priority_int),
            size=size_int,
            due_at=_get_due_at_from_str_arg(due_at_str),
        )
    )
    task = dart.update_task(id, task_update).item

    _log(f"Updated task\n\n  {task.title}\n  {task.html_url}\n  ID: {task.id}\n")
    _log("Done.")
    return task


def delete_task(id: str) -> Task:
    dart = Dart()
    task = dart.delete_task(id).item

    _log(f"Deleted task\n\n  {task.title}\n  {task.html_url}\n  ID: {task.id}\n")
    _log("Done.")
    return task


def create_doc(
    title: str,
    *,
    folder_title: Union[str, Unset] = UNSET,
    text: Union[str, Unset] = UNSET,
) -> Doc:
    dart = Dart()
    doc_create = WrappedDocCreate(item=DocCreate(title=title, folder=folder_title, text=text))
    doc = dart.create_doc(doc_create).item

    _log(f"Created doc\n\n  {doc.title}\n  {doc.html_url}\n  ID: {doc.id}\n")
    _log("Done.")
    return doc


def update_doc(
    id: str,
    *,
    title: str,
    folder_title: Union[str, Unset] = UNSET,
    text: Union[str, Unset] = UNSET,
) -> Doc:
    dart = Dart()
    doc_update = WrappedDocUpdate(item=DocUpdate(id, title=title, folder=folder_title, text=text))
    doc = dart.update_doc(id, doc_update).item

    _log(f"Updated doc\n\n  {doc.title}\n  {doc.html_url}\n  ID: {doc.id}\n")
    _log("Done.")
    return doc


def delete_doc(id: str) -> Doc:
    dart = Dart()
    doc = dart.delete_doc(id).item

    _log(f"Deleted doc\n\n  {doc.title}\n  {doc.html_url}\n  ID: {doc.id}\n")
    _log("Done.")
    return doc


def create_comment(id: str, text: str) -> Comment:
    dart = Dart()
    comment_create = WrappedCommentCreate(item=CommentCreate(task_id=id, text=text))
    comment = dart.create_comment(comment_create).item
    _log(f"Created comment\n\n  {comment.html_url}\n  ID: {comment.id}\n")
    _log("Done.")
    return comment


def server(
    *,
    port: int = _SERVER_DEFAULT_PORT,
    no_ngrok: bool = False,
    webhook: bool = False,
    response_str: Union[str, None] = None,
) -> None:
    """Run a simple Flask server, optionally tunneled with ngrok."""
    response: Union[dict, list, str, int, float, bool, None] = None
    if response_str is not None:
        try:
            response = json.loads(response_str)
        except json.JSONDecodeError as ex:
            _dart_exit(f"Invalid JSON for --response: {ex}.")
    run_server(port=port, no_ngrok=no_ngrok, webhook=webhook, response=response)


def _add_standard_task_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-d",
        "--dartboard",
        dest="dartboard_title",
        help="task dartboard title",
        default=UNSET,
    )
    parser.add_argument(
        "-s",
        "--status",
        dest="status_title",
        help="task status title",
        default=UNSET,
    )
    parser.add_argument(
        "-a",
        "--assignee",
        dest="assignee_emails",
        nargs="*",
        action="extend",
        help="task assignee email(s)",
    )
    parser.add_argument(
        "-t",
        "--tag",
        dest="tag_titles",
        nargs="*",
        action="extend",
        help="task tag title(s)",
    )
    parser.add_argument(
        "-p",
        "--priority",
        dest="priority_int",
        type=int,
        choices=_PRIORITY_MAP.keys(),
        help="task priority",
        default=UNSET,
    )
    parser.add_argument(
        "-i",
        "--size",
        dest="size_int",
        type=int,
        choices=_SIZES,
        help="task size",
        default=UNSET,
    )
    parser.add_argument(
        "-r",
        "--due-date",
        dest="due_at_str",
        help="task due date",
        default=UNSET,
    )


def cli() -> None:
    signal.signal(signal.SIGINT, _exit_gracefully)
    global _is_cli
    _is_cli = True

    version_check_thread = _start_version_check_thread()

    if _VERSION_CMD in sys.argv[1:]:
        print_version()
        _print_pending_version_message(version_check_thread)
        return

    parser = ArgumentParser(prog=_PROG, description="A CLI to interact with Dart")
    metavar = ",".join(
        [
            _LOGIN_CMD,
            _CREATE_AGENT_CMD,
            _UPDATE_AGENT_CMD,
            _DELETE_AGENT_CMD,
            _CONNECT_AGENT_CMD,
            _CREATE_TASK_CMD,
            _UPDATE_TASK_CMD,
            _DELETE_TASK_CMD,
            _BEGIN_TASK_CMD,
            _CREATE_DOC_CMD,
            _UPDATE_DOC_CMD,
            _DELETE_DOC_CMD,
            _CREATE_COMMENT_CMD,
            _SERVER_START_CMD,
        ]
    )
    subparsers = parser.add_subparsers(
        title="command",
        required=True,
        metavar=f"{{{metavar}}}",
    )

    get_host_parser = subparsers.add_parser(_GET_HOST_CMD, aliases=["hg"])
    get_host_parser.set_defaults(func=get_host)

    set_host_parser = subparsers.add_parser(_SET_HOST_CMD, aliases=["hs"])
    set_host_parser.add_argument("host", help="the new host: {prod|stag|dev|local|[URL]}")
    set_host_parser.set_defaults(func=set_host)

    login_parser = subparsers.add_parser(_LOGIN_CMD, aliases=["l"], help="login")
    login_parser.add_argument("-t", "--token", dest="token", help="your authentication token")
    login_parser.set_defaults(func=login)

    create_agent_parser = subparsers.add_parser(
        _CREATE_AGENT_CMD, aliases=["ac"], help=_HELP_TEXT_TO_COMMAND[_CREATE_AGENT_CMD]
    )
    create_agent_parser.add_argument("name", help="agent name")
    create_agent_parser.add_argument(
        "-m",
        "--execution-mode",
        dest="execution_mode",
        type=AgentExecutionMode,
        choices=list(AgentExecutionMode),
        help="agent execution mode",
        default=UNSET,
    )
    create_agent_parser.set_defaults(func=create_agent)

    update_agent_parser = subparsers.add_parser(
        _UPDATE_AGENT_CMD, aliases=["au"], help=_HELP_TEXT_TO_COMMAND[_UPDATE_AGENT_CMD]
    )
    update_agent_parser.add_argument("id", help="agent ID")
    update_agent_parser.add_argument("-n", "--name", dest="name", help="agent name", default=UNSET)
    update_agent_parser.add_argument(
        "-m",
        "--execution-mode",
        dest="execution_mode",
        type=AgentExecutionMode,
        choices=list(AgentExecutionMode),
        help="agent execution mode",
        default=UNSET,
    )
    update_agent_parser.set_defaults(func=update_agent)

    delete_agent_parser = subparsers.add_parser(
        _DELETE_AGENT_CMD, aliases=["ad"], help=_HELP_TEXT_TO_COMMAND[_DELETE_AGENT_CMD]
    )
    delete_agent_parser.add_argument("id", help="agent ID")
    delete_agent_parser.set_defaults(func=delete_agent)

    connect_agent_parser = subparsers.add_parser(
        _CONNECT_AGENT_CMD, aliases=["ax"], help="connect a local agent to a Dart agent"
    )
    connect_agent_parser.add_argument("id", nargs="?", help="agent ID")
    connect_agent_parser.add_argument(
        "-q",
        "--quiet",
        dest="quiet",
        action="store_true",
        help="hide incoming and outgoing websocket messages",
    )
    connect_agent_parser.set_defaults(func=connect_agent)

    create_task_parser = subparsers.add_parser(
        _CREATE_TASK_CMD, aliases=["tc"], help=_HELP_TEXT_TO_COMMAND[_CREATE_TASK_CMD]
    )
    create_task_parser.add_argument("title", help="task title")
    create_task_parser.add_argument(
        "-b",
        "--begin",
        dest="should_begin",
        action="store_true",
        help="begin work on the task after creation",
    )
    create_task_parser.add_argument(
        "--begin-status",
        dest="begin_status_name",
        help=f"status to move the task to when beginning (default: {_DEFAULT_BEGIN_STATUS})",
        default=_DEFAULT_BEGIN_STATUS,
    )
    _add_standard_task_arguments(create_task_parser)
    create_task_parser.set_defaults(func=create_task)

    update_task_parser = subparsers.add_parser(
        _UPDATE_TASK_CMD, aliases=["tu"], help=_HELP_TEXT_TO_COMMAND[_UPDATE_TASK_CMD]
    )
    update_task_parser.add_argument("id", help="task ID")
    update_task_parser.add_argument("-e", "--title", dest="title", help="task title", default=UNSET)
    _add_standard_task_arguments(update_task_parser)
    update_task_parser.set_defaults(func=update_task)

    delete_task_parser = subparsers.add_parser(
        _DELETE_TASK_CMD, aliases=["td"], help=_HELP_TEXT_TO_COMMAND[_DELETE_TASK_CMD]
    )
    delete_task_parser.add_argument("id", help="task ID")
    delete_task_parser.set_defaults(func=delete_task)

    begin_task_parser = subparsers.add_parser(_BEGIN_TASK_CMD, aliases=["tb"], help="begin work on a task")
    begin_task_parser.add_argument(
        "-s",
        "--status",
        dest="status_name",
        help=f"status to move the task to (default: {_DEFAULT_BEGIN_STATUS})",
        default=_DEFAULT_BEGIN_STATUS,
    )
    begin_task_parser.add_argument("-d", "--dartboard", dest="dartboard_title", help="dartboard title", default=UNSET)
    begin_task_parser.set_defaults(func=begin_task_interactive)

    create_doc_parser = subparsers.add_parser(
        _CREATE_DOC_CMD, aliases=["dc"], help=_HELP_TEXT_TO_COMMAND[_CREATE_DOC_CMD]
    )
    create_doc_parser.add_argument("title", help="doc title")
    create_doc_parser.add_argument("-f", "--folder", dest="folder_title", help="doc folder title", default=UNSET)
    create_doc_parser.add_argument("-t", "--text", dest="text", help="doc text", default=UNSET)
    create_doc_parser.set_defaults(func=create_doc)

    update_doc_parser = subparsers.add_parser(
        _UPDATE_DOC_CMD, aliases=["du"], help=_HELP_TEXT_TO_COMMAND[_UPDATE_DOC_CMD]
    )
    update_doc_parser.add_argument("id", help="doc ID")
    update_doc_parser.add_argument("-e", "--title", dest="title", help="doc title", default=UNSET)
    update_doc_parser.add_argument("-f", "--folder", dest="folder_title", help="doc folder title", default=UNSET)
    update_doc_parser.add_argument("-t", "--text", dest="text", help="doc text", default=UNSET)
    update_doc_parser.set_defaults(func=update_doc)

    delete_doc_parser = subparsers.add_parser(
        _DELETE_DOC_CMD, aliases=["dd"], help=_HELP_TEXT_TO_COMMAND[_DELETE_DOC_CMD]
    )
    delete_doc_parser.add_argument("id", help="doc ID")
    delete_doc_parser.set_defaults(func=delete_doc)

    create_comment_parser = subparsers.add_parser(
        _CREATE_COMMENT_CMD, aliases=["cc"], help=_HELP_TEXT_TO_COMMAND[_CREATE_COMMENT_CMD]
    )
    create_comment_parser.add_argument("id", help="task ID")
    create_comment_parser.add_argument("text", help="comment text")
    create_comment_parser.set_defaults(func=create_comment)

    server_parser = subparsers.add_parser(
        _SERVER_START_CMD, aliases=["ss"], help="run a simple HTTP server, optionally tunneled with ngrok"
    )
    server_parser.add_argument(
        "-p", "--port", dest="port", type=int, default=_SERVER_DEFAULT_PORT, help="port to listen on"
    )
    server_parser.add_argument(
        "-n", "--no-ngrok", dest="no_ngrok", action="store_true", help="don't try to start an ngrok tunnel"
    )
    server_parser.add_argument(
        "-w",
        "--webhook",
        dest="webhook",
        action="store_true",
        help="treat all requests as Dart webhook events instead of inspecting the Dart-Signature header",
    )
    server_parser.add_argument(
        "-r",
        "--response",
        dest="response_str",
        help='JSON to return for every request (default: {"ok": true})',
        default=None,
    )
    server_parser.set_defaults(func=server)

    args = vars(parser.parse_args())
    func = args.pop("func")
    try:
        func(**args)
    finally:
        _print_pending_version_message(version_check_thread)
