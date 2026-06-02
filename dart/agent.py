from __future__ import annotations

import asyncio
import contextlib
import json
import random
import shutil
import subprocess
import sys
import time
from typing import Any, Literal, Mapping
from urllib.parse import urlsplit, urlunsplit

from websockets.asyncio.client import connect as _websocket_connect
from websockets.exceptions import ConnectionClosed, InvalidStatus

from .exception import UNKNOWN_FAILURE_MESSAGE, AgentAuthError

_OutputMode = Literal["json", "jsonl"]

_WEBSOCKET_PATH = "/ws/v0/local-agent"
_AUTH_FAILURE_STATUS_CODES = (401, 403)
_RUN_TIMEOUT_SECONDS = 1800
_MAX_RECONNECT_DELAY_SECONDS = 15
_RECONNECT_TIMEOUT_SECONDS = 120

_LOCAL_AGENT_KEY = "localAgent"
_CHANGES_KEY = "changes"
_EXIT_KEY = "exit"
_MESSAGE_ID_KEY = "id"
_MESSAGE_KEY = "message"
_NAME_KEY = "name"
_PROMPT_KEY = "prompt"
_SUCCESS_KEY = "success"
_TITLE_KEY = "title"
_TYPE_KEY = "type"

_RESULT_TYPE = "result"
_START_TYPE = "start"
_UPDATE_TYPE = "update"
_WORK_TYPE = "message"

_CLOSE_ERROR_UNAUTHORIZED = "unauthorized"
_CLOSE_ERROR_AGENT_NOT_FOUND = "agent_not_found"
_CLOSE_ERROR_AGENT_NOT_LOCAL = "agent_not_local"
_CLOSE_ERROR_IN_USE = "agent_in_use"
_CLOSE_ERROR_INVALID_RESULT = "invalid_result"
_CLOSE_ERROR_UNKNOWN_WORK = "unknown_work"
_CLOSE_ERROR_CODES = {
    _CLOSE_ERROR_UNAUTHORIZED,
    _CLOSE_ERROR_AGENT_NOT_FOUND,
    _CLOSE_ERROR_AGENT_NOT_LOCAL,
    _CLOSE_ERROR_IN_USE,
    _CLOSE_ERROR_INVALID_RESULT,
    _CLOSE_ERROR_UNKNOWN_WORK,
}


class _LocalAgentSetupError(Exception):
    pass


class _LocalAgent:
    def __init__(
        self,
        *,
        start_command: tuple[str, ...],
        session_id_key: str,
        response_key: str | tuple[str, ...],
        output_mode: _OutputMode,
        resume_command: tuple[str, ...] | None = None,
        resume_suffix: tuple[str, ...] = (),
    ) -> None:
        self.start_command = start_command
        self.session_id_key = session_id_key
        self.response_keys = (response_key,) if isinstance(response_key, str) else response_key
        self.output_mode = output_mode
        self.resume_command = resume_command
        self.resume_suffix = resume_suffix

    def make_command(self, session_id: str | None, prompt: str) -> tuple[str, ...]:
        if session_id is not None and self.resume_command is not None:
            return (*self.resume_command, session_id, *self.resume_suffix, prompt)
        return (*self.start_command, prompt)

    def executable(self) -> str:
        return self.start_command[0]

    def is_available(self) -> bool:
        return shutil.which(self.executable()) is not None

    def parse_output(self, stdout: str, stderr: str) -> tuple[str, str | None]:
        response_parts_by_key = {response_key: [] for response_key in self.response_keys}
        session_id: str | None = None
        for value in _load_json_values(stdout, self.output_mode):
            if not isinstance(value, dict):
                continue
            session_id = session_id or _nested_string(value, self.session_id_key)
            for response_key in self.response_keys:
                response = _nested_string(value, response_key)
                if response:
                    response_parts_by_key[response_key].append(response)
                    break

        response = next(
            ("".join(response_parts).strip() for response_parts in response_parts_by_key.values() if response_parts),
            "",
        )
        if response:
            return response, session_id
        return "\n\n".join(part for part in (stdout.strip(), stderr.strip()) if part), session_id

    async def run(self, prompt: str, session_id: str | None) -> tuple[bool, str, str | None]:
        command = self.make_command(session_id, prompt)
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError:
            return False, f"Local agent command not found: {command[0]}.", None

        communicate_task = asyncio.create_task(process.communicate())
        timed_out = False
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(asyncio.shield(communicate_task), _RUN_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            timed_out = True
            with contextlib.suppress(ProcessLookupError):
                process.kill()
            stdout_bytes, stderr_bytes = await communicate_task
        except asyncio.CancelledError:
            with contextlib.suppress(ProcessLookupError):
                process.kill()
            with contextlib.suppress(Exception):
                await communicate_task
            raise

        stdout = stdout_bytes.decode(errors="replace").strip()
        stderr = stderr_bytes.decode(errors="replace").strip()
        output = "\n\n".join(part for part in (stdout, stderr) if part)

        if timed_out:
            message = f"{command[0]} did not finish within {_RUN_TIMEOUT_SECONDS} seconds."
            return False, "\n\n".join(part for part in (message, output) if part), None

        if process.returncode != 0:
            return False, output or f"{command[0]} exited with status {process.returncode}.", None

        message, next_session_id = self.parse_output(stdout, stderr)
        return True, message or "Done.", next_session_id


_LOCAL_AGENTS: dict[str, _LocalAgent] = {
    "claude": _LocalAgent(
        start_command=("claude", "-p", "--output-format", "json"),
        session_id_key="session_id",
        response_key="result",
        output_mode="json",
        resume_command=("claude", "-p", "--output-format", "json", "--resume"),
    ),
    "codex": _LocalAgent(
        start_command=("codex", "exec", "--json"),
        session_id_key="thread_id",
        response_key="item.text",
        output_mode="jsonl",
        resume_command=("codex", "exec", "--json", "resume"),
    ),
    "copilot": _LocalAgent(
        start_command=("copilot", "--output-format", "json", "-s", "--autopilot", "--no-ask-user", "--allow-all", "-p"),
        session_id_key="sessionId",
        response_key=("data.content", "data.summary"),
        output_mode="jsonl",
        resume_command=(
            "copilot",
            "--output-format",
            "json",
            "-s",
            "--autopilot",
            "--no-ask-user",
            "--allow-all",
            "--resume",
        ),
        resume_suffix=("-p",),
    ),
    "cursor": _LocalAgent(
        start_command=("cursor-agent", "--print", "--output-format", "json"),
        session_id_key="session_id",
        response_key="result",
        output_mode="json",
        resume_command=("cursor-agent", "--print", "--output-format", "json", "--resume"),
    ),
    "gemini": _LocalAgent(
        start_command=("gemini", "--output-format", "json", "-p"),
        session_id_key="session_id",
        response_key="response",
        output_mode="json",
    ),
    "opencode": _LocalAgent(
        start_command=("opencode", "run", "--format", "json"),
        session_id_key="sessionID",
        response_key="part.text",
        output_mode="jsonl",
        resume_command=("opencode", "run", "--format", "json", "--session"),
    ),
}
_LOCAL_AGENT_SESSION_IDS: dict[tuple[str, str], str] = {}


def connect_agent(agent_id: str, *, base_url: str, headers: Mapping[str, str], quiet: bool = False) -> None:
    try:
        asyncio.run(_connect_agent_async(agent_id, base_url=base_url, headers=headers, quiet=quiet))
    except KeyboardInterrupt:
        return
    except _LocalAgentSetupError as ex:
        raise SystemExit(str(ex)) from None


def _load_json_values(text: str, output_mode: _OutputMode) -> list[Any]:
    stripped_text = text.strip()
    if not stripped_text:
        return []

    if output_mode == "json":
        try:
            parsed = json.loads(stripped_text)
        except json.JSONDecodeError:
            return []
        return parsed if isinstance(parsed, list) else [parsed]

    values = []
    for line in stripped_text.splitlines():
        stripped_line = line.strip()
        if not stripped_line.startswith(("{", "[")):
            continue
        try:
            parsed_line = json.loads(stripped_line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed_line, list):
            values.extend(parsed_line)
        else:
            values.append(parsed_line)
    return values


def _nested_string(value: dict[str, Any], path: str) -> str | None:
    result: Any = value
    for key in path.split("."):
        if not isinstance(result, dict):
            return None
        result = result.get(key)
    return result if isinstance(result, str) and result else None


def _get_local_agent(local_agent_name: str) -> _LocalAgent:
    local_agent = _LOCAL_AGENTS.get(local_agent_name)
    if local_agent is None:
        raise _LocalAgentSetupError(f"Unknown local agent: {local_agent_name}.")
    return local_agent


def _validate_local_agent_available(local_agent_name: str) -> None:
    local_agent = _get_local_agent(local_agent_name)
    if not local_agent.is_available():
        raise _LocalAgentSetupError(f"Local agent command not found: {local_agent.executable()}.")


async def _run_local_agent(local_agent_name: str, prompt: str, message_id: str) -> tuple[bool, str]:
    local_agent = _get_local_agent(local_agent_name)
    session_key = (local_agent_name, message_id)
    success, message, session_id = await local_agent.run(prompt, _LOCAL_AGENT_SESSION_IDS.get(session_key))
    if success and session_id is not None:
        _LOCAL_AGENT_SESSION_IDS[session_key] = session_id
    return success, message


def _make_result_payload(work: dict[str, Any], success: bool, message: str) -> dict[str, Any]:
    return {
        _TYPE_KEY: _RESULT_TYPE,
        _MESSAGE_ID_KEY: work[_MESSAGE_ID_KEY],
        _SUCCESS_KEY: success,
        _MESSAGE_KEY: message,
    }


async def _handle_work(websocket: Any, work: dict[str, Any], quiet: bool) -> None:
    if not quiet:
        print(f"\nUser: {work[_PROMPT_KEY]}", flush=True)

    success, message = await _run_local_agent(work[_LOCAL_AGENT_KEY], work[_PROMPT_KEY], work[_MESSAGE_ID_KEY])
    result = _make_result_payload(work, success, message)
    if not quiet:
        print(f"\nAssistant: {message}", flush=True)
    await websocket.send(json.dumps(result))


async def _wait_for_stdin_eof() -> None:
    loop = asyncio.get_running_loop()
    future: asyncio.Future[None] = loop.create_future()

    def _on_stdin_ready() -> None:
        if sys.stdin.readline() == "" and not future.done():
            future.set_result(None)

    loop.add_reader(sys.stdin.fileno(), _on_stdin_ready)
    try:
        await future
    finally:
        loop.remove_reader(sys.stdin.fileno())


def _make_agent_url(base_url: str, agent_id: str) -> str:
    return f"{base_url.rstrip('/')}/a/{agent_id}"


def _print_start_message(message: dict[str, Any], agent_id: str, base_url: str) -> None:
    agent_url = _make_agent_url(base_url, agent_id)
    print(
        f"Connected agent\n\n  {message[_NAME_KEY]}\n  {agent_url}\n  ID: {agent_id}\n  Local agent: {message[_LOCAL_AGENT_KEY]}\n\nWaiting for work from Dart",
        flush=True,
    )


def _print_update(message: dict[str, Any]) -> bool:
    title = message.get(_TITLE_KEY)
    if not isinstance(title, str) or not title:
        title = "Agent updated"

    changes = message.get(_CHANGES_KEY)
    if not isinstance(changes, list):
        changes = []
    changes = [change for change in changes if isinstance(change, str) and change]

    if changes:
        print(f"\n{title}\n\n" + "\n".join(f"  {change}" for change in changes), flush=True)
    else:
        print(f"\n{title}", flush=True)
    return message.get(_EXIT_KEY) is True


async def _handle_messages(websocket: Any, quiet: bool, agent_id: str, base_url: str) -> bool:
    async for raw_message in websocket:
        message = json.loads(raw_message)
        message_type = message[_TYPE_KEY]
        if message_type == _START_TYPE:
            _validate_local_agent_available(message[_LOCAL_AGENT_KEY])
            _print_start_message(message, agent_id, base_url)
            continue
        if message_type == _UPDATE_TYPE:
            if _print_update(message):
                await websocket.close()
                return False
            continue
        if message_type != _WORK_TYPE:
            continue
        await _handle_work(websocket, message, quiet)
    return True


async def _run_until_closed_or_eof(websocket: Any, quiet: bool, *, agent_id: str, base_url: str) -> bool:
    messages_task = asyncio.create_task(_handle_messages(websocket, quiet, agent_id, base_url))
    if not sys.stdin.isatty():
        return await messages_task

    eof_task = asyncio.create_task(_wait_for_stdin_eof())
    done, pending = await asyncio.wait({messages_task, eof_task}, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
    for task in pending:
        with contextlib.suppress(asyncio.CancelledError):
            await task

    if eof_task in done:
        await websocket.close()
        return False
    return messages_task.result()


def _make_websocket_url(base_url: str, agent_id: str) -> str:
    parsed_url = urlsplit(base_url)
    scheme = "wss" if parsed_url.scheme == "https" else "ws"
    return urlunsplit((scheme, parsed_url.netloc, f"{_WEBSOCKET_PATH}/{agent_id}", "", ""))


def _make_origin(websocket_url: str) -> str:
    parsed_url = urlsplit(websocket_url)
    scheme = "https" if parsed_url.scheme == "wss" else "http"
    return f"{scheme}://{parsed_url.netloc}"


def _make_connection_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {key: value for key, value in headers.items() if key.lower() != "origin"}


def _raise_for_connection_closed_error(ex: ConnectionClosed) -> None:
    close_frame = getattr(ex, "rcvd", None)
    reason = getattr(close_frame, "reason", "") or getattr(ex, "reason", "")
    if not reason:
        return

    try:
        payload = json.loads(reason)
    except json.JSONDecodeError:
        return

    if not isinstance(payload, dict):
        return

    code = payload.get("code")
    message = payload.get("message")
    if code not in _CLOSE_ERROR_CODES or not isinstance(message, str) or not message:
        return

    if code == _CLOSE_ERROR_UNAUTHORIZED:
        raise AgentAuthError(message) from None
    raise SystemExit(message) from None


async def _connect_agent_async(agent_id: str, *, base_url: str, headers: Mapping[str, str], quiet: bool) -> None:
    websocket_url = _make_websocket_url(base_url, agent_id)
    reconnect_started_at: float | None = None
    reconnect_attempt = 0
    connection_headers = _make_connection_headers(headers)
    try:
        while True:
            try:
                async with _websocket_connect(
                    websocket_url,
                    additional_headers=connection_headers,
                    origin=_make_origin(websocket_url),
                ) as websocket:
                    reconnect_started_at = None
                    reconnect_attempt = 0
                    if not await _run_until_closed_or_eof(websocket, quiet, agent_id=agent_id, base_url=base_url):
                        return
            except ConnectionClosed as ex:
                _raise_for_connection_closed_error(ex)
            except (OSError, TimeoutError):
                pass

            if reconnect_started_at is None:
                reconnect_started_at = time.monotonic()
            if time.monotonic() - reconnect_started_at >= _RECONNECT_TIMEOUT_SECONDS:
                raise SystemExit("Could not reconnect to Dart agent.") from None

            reconnect_attempt += 1
            delay = min(2 ** (reconnect_attempt - 1), _MAX_RECONNECT_DELAY_SECONDS)
            delay += random.uniform(0, delay * 0.25)
            print(f"Connection unavailable, retrying in {delay:.1f}s", flush=True)
            await asyncio.sleep(delay)
    except InvalidStatus as ex:
        if ex.response.status_code in _AUTH_FAILURE_STATUS_CODES:
            raise AgentAuthError("Authentication failed, sign in again") from None
        raise SystemExit(UNKNOWN_FAILURE_MESSAGE) from None
