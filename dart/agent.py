from __future__ import annotations

import asyncio
import contextlib
import json
import random
import sys
import time
from typing import Any, Literal, Mapping
from urllib.parse import urlsplit, urlunsplit

from websockets.asyncio.client import connect as _websocket_connect
from websockets.exceptions import ConnectionClosed, InvalidStatus

_MESSAGE_ID_KEY = "id"
_LOCAL_AGENT_KEY = "localAgent"
_MESSAGE_KEY = "message"
_NAME_KEY = "name"
_PROMPT_KEY = "prompt"
_SUCCESS_KEY = "success"
_TYPE_KEY = "type"
_RESULT_TYPE = "result"
_START_TYPE = "start"
_AGENT_WEBSOCKET_PATH = "/ws/v0/local-agent"
_AUTH_FAILURE_STATUS_CODES = (401, 403)
_OutputMode = Literal["json", "jsonl"]


class AgentAuthError(Exception):
    pass


class _LocalAgent:
    def __init__(
        self,
        *,
        start_command: tuple[str, ...],
        session_id_key: str,
        response_key: str,
        output_mode: _OutputMode,
        resume_command: tuple[str, ...] | None = None,
        resume_suffix: tuple[str, ...] = (),
    ) -> None:
        self.start_command = start_command
        self.session_id_key = session_id_key
        self.response_key = response_key
        self.output_mode = output_mode
        self.resume_command = resume_command
        self.resume_suffix = resume_suffix

    def make_command(self, session_id: str | None, prompt: str) -> tuple[str, ...]:
        if session_id is not None and self.resume_command is not None:
            return (*self.resume_command, session_id, *self.resume_suffix, prompt)
        return (*self.start_command, prompt)

    def parse_output(self, stdout: str, stderr: str) -> tuple[str, str | None]:
        response_parts = []
        session_id: str | None = None
        for value in _load_json_values(stdout, self.output_mode):
            if not isinstance(value, dict):
                continue
            session_id = session_id or _nested_string(value, self.session_id_key)
            response = _nested_string(value, self.response_key)
            if response:
                response_parts.append(response)

        response = "".join(response_parts).strip()
        if response:
            return response, session_id
        if stdout.strip():
            return stdout.strip(), session_id
        return stderr.strip(), session_id

    async def run(self, prompt: str, session_id: str | None) -> tuple[bool, str, str | None]:
        command = self.make_command(session_id, prompt)
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError:
            return False, f"Local agent command not found: {command[0]}.", None

        stdout_bytes, stderr_bytes = await process.communicate()
        stdout = stdout_bytes.decode(errors="replace").strip()
        stderr = stderr_bytes.decode(errors="replace").strip()
        output = "\n\n".join(part for part in (stdout, stderr) if part)

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
_RECONNECT_TIMEOUT_SECONDS = 120
_MAX_RECONNECT_DELAY_SECONDS = 15


def connect_agent(agent_id: str, *, base_url: str, headers: Mapping[str, str], quiet: bool = False) -> None:
    try:
        asyncio.run(_connect_agent_async(agent_id, base_url=base_url, headers=headers, quiet=quiet))
    except KeyboardInterrupt:
        return


def _load_json_values(text: str, output_mode: _OutputMode) -> list[Any]:
    stripped_text = text.strip()
    if not stripped_text:
        return []

    if output_mode == "json":
        parsed = json.loads(stripped_text)
        return parsed if isinstance(parsed, list) else [parsed]

    values = []
    for line in stripped_text.splitlines():
        stripped_line = line.strip()
        if not stripped_line.startswith(("{", "[")):
            continue
        parsed_line = json.loads(stripped_line)
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


async def _run_local_agent(local_agent_name: str, prompt: str, message_id: str) -> tuple[bool, str]:
    local_agent = _LOCAL_AGENTS.get(local_agent_name)
    if local_agent is None:
        return False, f"Unknown local agent: {local_agent_name}."

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


def _print_start_message(message: dict[str, Any]) -> None:
    print(f"Connected {message[_NAME_KEY]} ({message[_LOCAL_AGENT_KEY]}), waiting for work", flush=True)


async def _handle_messages(websocket: Any, quiet: bool) -> None:
    async for raw_message in websocket:
        message = json.loads(raw_message)
        if message[_TYPE_KEY] == _START_TYPE:
            _print_start_message(message)
            continue
        await _handle_work(websocket, message, quiet)


async def _run_until_closed_or_eof(websocket: Any, quiet: bool) -> bool:
    messages_task = asyncio.create_task(_handle_messages(websocket, quiet))
    if not sys.stdin.isatty():
        await messages_task
        return True

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
    messages_task.result()
    return True


def _make_websocket_url(base_url: str, agent_id: str) -> str:
    parsed_url = urlsplit(base_url)
    scheme = "wss" if parsed_url.scheme == "https" else "ws"
    return urlunsplit((scheme, parsed_url.netloc, f"{_AGENT_WEBSOCKET_PATH}/{agent_id}", "", ""))


def _make_origin(websocket_url: str) -> str:
    parsed_url = urlsplit(websocket_url)
    scheme = "https" if parsed_url.scheme == "wss" else "http"
    return f"{scheme}://{parsed_url.netloc}"


def _make_connection_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {key: value for key, value in headers.items() if key.lower() != "origin"}


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
                    if not await _run_until_closed_or_eof(websocket, quiet):
                        return
            except (ConnectionClosed, OSError, TimeoutError):
                pass

            if reconnect_started_at is None:
                reconnect_started_at = time.monotonic()
            if time.monotonic() - reconnect_started_at >= _RECONNECT_TIMEOUT_SECONDS:
                raise SystemExit("Could not reconnect to Dart local agent.") from None

            reconnect_attempt += 1
            delay = min(2 ** (reconnect_attempt - 1), _MAX_RECONNECT_DELAY_SECONDS)
            delay += random.uniform(0, delay * 0.25)
            print(f"Connection unavailable, retrying in {delay:.1f}s", flush=True)
            await asyncio.sleep(delay)
    except InvalidStatus as ex:
        if ex.response.status_code in _AUTH_FAILURE_STATUS_CODES:
            raise AgentAuthError from None
        raise SystemExit(f"Dart rejected the local-agent connection with HTTP {ex.response.status_code}.") from None
