from __future__ import annotations

import asyncio
import contextlib
import json
import os
import random
import shutil
import subprocess
import sys
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Literal, Mapping
from urllib.parse import urlsplit, urlunsplit

from websockets.asyncio.client import connect as _websocket_connect
from websockets.exceptions import ConnectionClosed, InvalidStatus

from .exception import UNKNOWN_FAILURE_MESSAGE, AgentAuthError

_OutputMode = Literal["json", "jsonl"]
AgentInstallPolicy = Literal["prompt", "auto", "never"]
AGENT_INSTALL_POLICIES: tuple[AgentInstallPolicy, ...] = ("prompt", "auto", "never")

_WEBSOCKET_PATH = "/ws/v0/local-agent"
_AUTH_FAILURE_STATUS_CODES = (401, 403)
_RUN_TIMEOUT_SECONDS = 1800
_STREAM_READ_CHUNK_SIZE_BYTES = 65536
_MAX_RECONNECT_DELAY_SECONDS = 15
_RECONNECT_TIMEOUT_SECONDS = 120

_LOCAL_AGENT_KEY = "localAgent"
_CHANGES_KEY = "changes"
_EXIT_KEY = "exit"
_KIND_KEY = "kind"
_MESSAGE_ID_KEY = "id"
_MESSAGE_KEY = "message"
_NAME_KEY = "name"
_PROMPT_KEY = "prompt"
_SUCCESS_KEY = "success"
_TITLE_KEY = "title"
_TYPE_KEY = "type"

_DONE_EVENT_KIND = "done"
_EVENT_KEY = "event"
_EVENT_TYPE = "event"
_SEQUENCE_KEY = "sequence"
_START_TYPE = "start"
_TEXT_DELTA_EVENT_KIND = "text_delta"
_THINKING_EVENT_KIND = "thinking"
_TOOL_CALL_EVENT_KIND = "tool_call"
_TOOL_ERROR_EVENT_KIND = "tool_error"
_TOOL_RESULT_EVENT_KIND = "tool_result"
_UPDATE_TYPE = "update"
_WORK_TYPE = "message"
_EVENT_SOURCE_KEY = "_localEventSource"
_DEFAULT_TEXT_EVENT_SOURCE = "__default_text__"
_STREAM_EVENT_TYPE = "stream_event"
_MESSAGE_START_EVENT_TYPE = "message_start"
_CONTENT_BLOCK_DELTA_EVENT_TYPE = "content_block_delta"
_TEXT_DELTA_DELTA_TYPE = "text_delta"
_CLAUDE_CONTENT_BLOCK_PATHS = (
    "message.content",
    "item.message.content",
    "data.message.content",
    "content",
    "content_block",
    "delta",
)
_TOOL_NAME_ALIASES = {
    "createPlanToolCall": "Plan",
    "deleteToolCall": "Delete",
    "editToolCall": "Edit",
    "globToolCall": "Glob",
    "grepToolCall": "Grep",
    "lsToolCall": "List",
    "mcpToolCall": "MCP",
    "readLintsToolCall": "Read lints",
    "readTodosToolCall": "Read todos",
    "readToolCall": "Read",
    "semSearchToolCall": "Search",
    "shellToolCall": "Bash",
    "updateTodosToolCall": "Update todos",
    "writeToolCall": "Write",
}

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
_LocalEventSender = Callable[[dict[str, Any]], Awaitable[None]]


class _LocalAgentSetupError(Exception):
    pass


@dataclass(frozen=True)
class _LocalAgentInstallCommand:
    command: tuple[str, ...]
    display: str
    windows_override: "_LocalAgentInstallCommand | None" = None

    @property
    def current(self) -> "_LocalAgentInstallCommand":
        if os.name == "nt" and self.windows_override is not None:
            return self.windows_override
        return self


class _LocalAgent:
    def __init__(
        self,
        *,
        display_name: str,
        start_command: tuple[str, ...],
        install_command: _LocalAgentInstallCommand,
        session_id_key: str,
        response_key: str | tuple[str, ...],
        output_mode: _OutputMode,
        resume_command: tuple[str, ...] | None = None,
        resume_suffix: tuple[str, ...] = (),
        response_types: tuple[str, ...] | None = None,
        response_phases: tuple[str, ...] | None = None,
        stream_response_keys: bool = True,
        deduplicate_stream_events: bool = False,
        reassemble_stream_events: bool = False,
    ) -> None:
        self.display_name = display_name
        self.start_command = start_command
        self.install_command = install_command
        self.session_id_key = session_id_key
        self.response_keys = (response_key,) if isinstance(response_key, str) else response_key
        self.output_mode = output_mode
        self.resume_command = resume_command
        self.resume_suffix = resume_suffix
        self.response_types = response_types
        self.response_phases = response_phases
        self.stream_response_keys = stream_response_keys
        self.deduplicate_stream_events = deduplicate_stream_events
        self.reassemble_stream_events = reassemble_stream_events

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
            if not self._should_use_response_value(value):
                continue
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

    def events_from_value(self, value: dict[str, Any]) -> list[dict[str, Any]]:
        return [_strip_internal_event_keys(event) for event in self._events_from_value(value)]

    def _events_from_value(
        self, value: dict[str, Any], stream_assembler: "_StreamEventAssembler | None" = None
    ) -> list[dict[str, Any]]:
        if stream_assembler is not None and _nested_string(value, _TYPE_KEY) == _STREAM_EVENT_TYPE:
            return stream_assembler.events_from_stream_event(value)

        content_block_events = _events_from_content_blocks(
            value,
            fallback_message_id=stream_assembler.message_id if stream_assembler is not None else "",
        )
        if content_block_events:
            return content_block_events

        if self.stream_response_keys and (response := self._response_text_from_value(value)):
            return [{_KIND_KEY: _TEXT_DELTA_EVENT_KIND, "text": response}]

        value_types = " ".join(
            _string_from_paths(
                value,
                ("kind", "type", "subtype", "event", "item.type", "item.subtype", "data.type", "data.subtype"),
            )
        ).lower()
        summary = _summary_from_value(value)
        if "thinking" in value_types or "reasoning" in value_types:
            detail = _first_string_from_paths(
                value,
                ("detail", "text", "content", "message", "item.detail", "item.text", "item.content", "data.content"),
            )
            if detail:
                event: dict[str, Any] = {_KIND_KEY: _THINKING_EVENT_KIND, "detail": detail}
                summary_text = _first_string_from_paths(value, ("summary", "item.summary", "data.summary"))
                if summary_text:
                    event["summary"] = summary_text
                return [event]

        if "tool" not in value_types and "function" not in value_types:
            return []

        tool_call_id = _first_string_from_paths(
            value,
            (
                "toolCallId",
                "tool_call_id",
                "call_id",
                "item.toolCallId",
                "item.tool_call_id",
                "item.call_id",
                "item.id",
                "data.toolCallId",
                "data.tool_call_id",
                "data.call_id",
                "data.id",
                "id",
            ),
        )
        tool_name = _first_string_from_paths(
            value,
            (
                "name",
                "tool_name",
                "toolName",
                "function.name",
                "item.name",
                "item.tool_name",
                "item.toolName",
                "item.function.name",
                "data.name",
                "data.tool_name",
                "data.toolName",
                "data.function.name",
                "tool_call.name",
                "tool_call.tool.name",
                "tool_call.tool.case",
            ),
        )
        if not tool_call_id:
            return []
        if tool_name:
            tool_name = _normalized_tool_name(tool_name)

        common: dict[str, Any] = {"toolCallId": tool_call_id, "name": tool_name or "tool"}
        if summary:
            common["summary"] = summary

        if "error" in value_types:
            error = _first_string_from_paths(value, ("error", "message", "item.error", "item.message", "data.error"))
            if error:
                return [{_KIND_KEY: _TOOL_ERROR_EVENT_KIND, **common, "error": error}]

        if "result" in value_types or "return" in value_types or "complete" in value_types or "finish" in value_types:
            result = _first_dict_from_paths(
                value,
                (
                    "result",
                    "content",
                    "item.result",
                    "item.content",
                    "data.result",
                    "tool_call.result",
                    "tool_call.tool.value.result",
                ),
            )
            if result is None:
                result_text = _first_string_from_paths(
                    value, ("result", "content", "message", "item.result", "item.content", "data.result")
                )
                result = {"content": result_text} if result_text else {}
            return [{_KIND_KEY: _TOOL_RESULT_EVENT_KIND, **common, "result": result}]

        if "call" in value_types or "start" in value_types:
            if not tool_name:
                return []
            args = _first_dict_from_paths(
                value,
                (
                    "args",
                    "arguments",
                    "input",
                    "function.arguments",
                    "item.args",
                    "item.arguments",
                    "item.input",
                    "item.function.arguments",
                    "data.args",
                    "data.arguments",
                    "data.input",
                    "data.function.arguments",
                    "tool_call.args",
                    "tool_call.arguments",
                    "tool_call.input",
                    "tool_call.function.arguments",
                    "tool_call.tool.value.args",
                ),
            )
            return [{_KIND_KEY: _TOOL_CALL_EVENT_KIND, **common, "args": args or {}}]

        return []

    def _response_text_from_value(self, value: dict[str, Any]) -> str | None:
        if not self._should_use_response_value(value):
            return None
        for response_key in self.response_keys:
            response = _nested_string(value, response_key)
            if response:
                return response
        return None

    def _should_use_response_value(self, value: dict[str, Any]) -> bool:
        if self.response_types is not None:
            value_type = _nested_string(value, _TYPE_KEY)
            if value_type not in self.response_types:
                return False
        if self.response_phases is not None:
            phase = _nested_string(value, "data.phase")
            if phase not in self.response_phases:
                return False
        return True

    async def run(
        self, prompt: str, session_id: str | None, emit_event: _LocalEventSender
    ) -> tuple[bool, str, str | None]:
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

        assert process.stdout is not None
        assert process.stderr is not None
        next_session_id = session_id
        stream_state = _StreamEventState(deduplicate_cumulative_events=self.deduplicate_stream_events)
        stream_assembler = _StreamEventAssembler() if self.reassemble_stream_events else None

        async def handle_stdout_line(line: str) -> None:
            nonlocal next_session_id
            if self.output_mode != "jsonl":
                return
            for value in _load_json_values(line, self.output_mode):
                if not isinstance(value, dict):
                    continue
                next_session_id = next_session_id or _nested_string(value, self.session_id_key)
                for event in self._events_from_value(value, stream_assembler):
                    prepared_event = stream_state.prepare(event)
                    if prepared_event is not None:
                        await emit_event(prepared_event)

        stdout_task = asyncio.create_task(_read_stream(process.stdout, handle_stdout_line))
        stderr_task = asyncio.create_task(_read_stream(process.stderr))
        wait_task = asyncio.create_task(process.wait())
        run_task = asyncio.gather(wait_task, stdout_task, stderr_task)
        timed_out = False
        try:
            await asyncio.wait_for(asyncio.shield(run_task), _RUN_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            timed_out = True
            with contextlib.suppress(ProcessLookupError):
                process.kill()
            await asyncio.gather(wait_task, stdout_task, stderr_task, return_exceptions=True)
        except asyncio.CancelledError:
            with contextlib.suppress(ProcessLookupError):
                process.kill()
            with contextlib.suppress(Exception):
                await asyncio.gather(wait_task, stdout_task, stderr_task, return_exceptions=True)
            raise
        except Exception:
            with contextlib.suppress(ProcessLookupError):
                process.kill()
            with contextlib.suppress(Exception):
                await asyncio.gather(wait_task, stdout_task, stderr_task, return_exceptions=True)
            raise

        stdout = stdout_task.result().strip()
        stderr = stderr_task.result().strip()
        output = "\n\n".join(part for part in (stdout, stderr) if part)

        if timed_out:
            message = f"{command[0]} did not finish within {_RUN_TIMEOUT_SECONDS} seconds."
            return False, "\n\n".join(part for part in (message, output) if part), None

        if process.returncode != 0:
            return False, output or f"{command[0]} exited with status {process.returncode}.", None

        message, parsed_session_id = self.parse_output(stdout, stderr)
        next_session_id = parsed_session_id or next_session_id
        if message and not stream_state.has_streamed_text:
            await emit_event({_KIND_KEY: _TEXT_DELTA_EVENT_KIND, "text": message})
        return True, message or "Done.", next_session_id


def _npm_install_command(package: str) -> _LocalAgentInstallCommand:
    return _LocalAgentInstallCommand(("npm", "install", "-g", package), f"npm install -g {package}")


_LOCAL_AGENTS: dict[str, _LocalAgent] = {
    "claude": _LocalAgent(
        display_name="Claude Code",
        start_command=(
            "claude",
            "-p",
            "--dangerously-skip-permissions",
            "--output-format",
            "stream-json",
            "--include-partial-messages",
            "--verbose",
        ),
        install_command=_npm_install_command("@anthropic-ai/claude-code"),
        session_id_key="session_id",
        response_key="result",
        output_mode="jsonl",
        resume_command=(
            "claude",
            "-p",
            "--dangerously-skip-permissions",
            "--output-format",
            "stream-json",
            "--include-partial-messages",
            "--verbose",
            "--resume",
        ),
        stream_response_keys=False,
        deduplicate_stream_events=True,
        reassemble_stream_events=True,
    ),
    "codex": _LocalAgent(
        display_name="Codex",
        start_command=(
            "codex",
            "exec",
            "--json",
            "--dangerously-bypass-approvals-and-sandbox",
            "--skip-git-repo-check",
        ),
        install_command=_npm_install_command("@openai/codex"),
        session_id_key="thread_id",
        response_key="item.text",
        output_mode="jsonl",
        resume_command=(
            "codex",
            "exec",
            "--json",
            "--dangerously-bypass-approvals-and-sandbox",
            "--skip-git-repo-check",
            "resume",
        ),
    ),
    "copilot": _LocalAgent(
        display_name="GitHub Copilot CLI",
        start_command=("copilot", "--output-format", "json", "-s", "--autopilot", "--no-ask-user", "--allow-all", "-p"),
        install_command=_npm_install_command("@github/copilot"),
        session_id_key="sessionId",
        response_key="data.content",
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
        response_types=("assistant.message",),
        response_phases=("final_answer",),
    ),
    "cursor": _LocalAgent(
        display_name="Cursor CLI",
        start_command=("cursor-agent", "--print", "--force", "--output-format", "stream-json"),
        install_command=_LocalAgentInstallCommand(
            ("sh", "-c", "curl https://cursor.com/install -fsS | bash"),
            "curl https://cursor.com/install -fsS | bash",
            windows_override=_LocalAgentInstallCommand(
                (
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    "irm 'https://cursor.com/install?win32=true' | iex",
                ),
                "irm 'https://cursor.com/install?win32=true' | iex",
            ),
        ),
        session_id_key="session_id",
        response_key="result",
        output_mode="jsonl",
        resume_command=("cursor-agent", "--print", "--force", "--output-format", "stream-json", "--resume"),
        stream_response_keys=False,
    ),
    "gemini": _LocalAgent(
        display_name="Gemini CLI",
        start_command=("gemini", "--output-format", "json", "--approval-mode", "yolo", "--skip-trust", "-p"),
        install_command=_npm_install_command("@google/gemini-cli"),
        session_id_key="session_id",
        response_key="response",
        output_mode="json",
    ),
    "opencode": _LocalAgent(
        display_name="OpenCode",
        start_command=("opencode", "run", "--format", "json", "--dangerously-skip-permissions"),
        install_command=_npm_install_command("opencode-ai"),
        session_id_key="sessionID",
        response_key="part.text",
        output_mode="jsonl",
        resume_command=("opencode", "run", "--format", "json", "--dangerously-skip-permissions", "--session"),
    ),
}
_LOCAL_AGENT_SESSION_IDS: dict[tuple[str, str], str] = {}


def connect_agent(
    agent_id: str,
    install: AgentInstallPolicy,
    *,
    base_url: str,
    headers: Mapping[str, str],
    quiet: bool = False,
) -> None:
    try:
        asyncio.run(_connect_agent_async(agent_id, install, base_url=base_url, headers=headers, quiet=quiet))
    except KeyboardInterrupt:
        return
    except _LocalAgentSetupError as ex:
        raise SystemExit(str(ex)) from None


def ensure_local_agent_available(local_agent_name: str, install: AgentInstallPolicy) -> None:
    try:
        _validate_local_agent_available(local_agent_name, install)
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


async def _read_stream(stream: asyncio.StreamReader, on_line: Callable[[str], Awaitable[None]] | None = None) -> str:
    chunks = []
    pending = b""
    while True:
        chunk = await stream.read(_STREAM_READ_CHUNK_SIZE_BYTES)
        if not chunk:
            break

        chunks.append(chunk)
        pending += chunk
        while b"\n" in pending:
            line_bytes, pending = pending.split(b"\n", 1)
            line = line_bytes.decode(errors="replace") + "\n"
            if on_line is not None:
                await on_line(line)

    if pending and on_line is not None:
        line = pending.decode(errors="replace")
        await on_line(line)

    return b"".join(chunks).decode(errors="replace")


def _nested_value(value: dict[str, Any], path: str) -> Any:
    result: Any = value
    for key in path.split("."):
        if not isinstance(result, dict):
            return None
        result = result.get(key)
    return result


def _nested_string(value: dict[str, Any], path: str) -> str | None:
    result = _nested_value(value, path)
    return result if isinstance(result, str) and result else None


def _string_from_paths(value: dict[str, Any], paths: tuple[str, ...]) -> list[str]:
    return [result for path in paths if (result := _nested_string(value, path))]


def _first_string_from_paths(value: dict[str, Any], paths: tuple[str, ...]) -> str | None:
    return next(iter(_string_from_paths(value, paths)), None)


def _first_dict_from_paths(value: dict[str, Any], paths: tuple[str, ...]) -> dict[str, Any] | None:
    for path in paths:
        result = _nested_value(value, path)
        if isinstance(result, dict):
            return result
    return None


def _summary_from_value(value: dict[str, Any]) -> list[Any] | None:
    for path in ("summary", "item.summary", "data.summary"):
        result = _nested_value(value, path)
        if isinstance(result, list):
            return result
        if isinstance(result, str) and result:
            return [result]
    return None


def _normalized_tool_name(tool_name: str) -> str:
    return _TOOL_NAME_ALIASES.get(tool_name, tool_name)


def _events_from_content_blocks(value: dict[str, Any], *, fallback_message_id: str = "") -> list[dict[str, Any]]:
    events = []
    for source, block in _content_blocks_from_value(value, fallback_message_id=fallback_message_id):
        event = _event_from_content_block(block)
        if event is not None and _should_emit_content_block_event(value, event):
            event[_EVENT_SOURCE_KEY] = source
            events.append(event)
    return events


def _should_emit_content_block_event(value: dict[str, Any], event: dict[str, Any]) -> bool:
    if not _is_user_message_value(value):
        return True
    return event.get(_KIND_KEY) in {_TOOL_RESULT_EVENT_KIND, _TOOL_ERROR_EVENT_KIND}


def _is_user_message_value(value: dict[str, Any]) -> bool:
    for path in ("role", "message.role", "item.role", "data.role"):
        role = _nested_string(value, path)
        if role is not None and role.lower() == "user":
            return True

    value_type = _nested_string(value, _TYPE_KEY)
    return value_type is not None and value_type.lower().startswith("user")


def _content_blocks_from_value(
    value: dict[str, Any], *, fallback_message_id: str = ""
) -> list[tuple[str, dict[str, Any]]]:
    blocks: list[tuple[str, dict[str, Any]]] = []
    message_id = (
        _first_string_from_paths(value, ("message.id", "item.message.id", "data.message.id", "id"))
        or fallback_message_id
    )
    if _is_content_block(value):
        blocks.append((_content_block_source(message_id, "self", 0, value), value))

    for path in _CLAUDE_CONTENT_BLOCK_PATHS:
        candidate = _nested_value(value, path)
        if isinstance(candidate, list):
            blocks.extend(
                (_content_block_source(message_id, path, index, block), block)
                for index, block in enumerate(candidate)
                if isinstance(block, dict) and _is_content_block(block)
            )
        elif isinstance(candidate, dict) and _is_content_block(candidate):
            blocks.append((_content_block_source(message_id, path, 0, candidate), candidate))

    return blocks


def _content_block_source(message_id: str, path: str, index: int, block: dict[str, Any]) -> str:
    block_id = _tool_call_id_from_block(block) or _first_string_from_paths(block, ("id",))
    if block_id:
        return f"{path}:{block_id}"
    return f"{message_id}:{path}:{index}"


def _is_content_block(value: dict[str, Any]) -> bool:
    block_type = _content_block_type(value)
    return (
        block_type in {"text", "text_delta", "thinking", "thinking_delta", "reasoning", "reasoning_delta"}
        or _is_tool_call_type(block_type)
        or _is_tool_result_type(block_type)
    )


def _content_block_type(value: dict[str, Any]) -> str:
    block_type = value.get("type")
    return block_type.lower() if isinstance(block_type, str) else ""


def _event_from_content_block(block: dict[str, Any]) -> dict[str, Any] | None:
    block_type = _content_block_type(block)
    if block_type in {"text", "text_delta"}:
        text = _first_string_from_paths(block, ("text", "content"))
        return {_KIND_KEY: _TEXT_DELTA_EVENT_KIND, "text": text} if text else None

    if block_type in {"thinking", "thinking_delta", "reasoning", "reasoning_delta"}:
        detail = _first_string_from_paths(block, ("thinking", "detail", "text", "content"))
        if not detail:
            return None
        event: dict[str, Any] = {_KIND_KEY: _THINKING_EVENT_KIND, "detail": detail}
        summary = _first_string_from_paths(block, ("summary",))
        if summary:
            event["summary"] = summary
        return event

    if _is_tool_call_type(block_type):
        tool_call_id = _tool_call_id_from_block(block)
        tool_name = _tool_name_from_block(block)
        if not tool_call_id or not tool_name:
            return None
        tool_name = _normalized_tool_name(tool_name)
        event = {
            _KIND_KEY: _TOOL_CALL_EVENT_KIND,
            "toolCallId": tool_call_id,
            "name": tool_name,
            "args": _tool_args_from_block(block),
        }
        _add_tool_summary(event, block)
        return event

    if _is_tool_result_type(block_type):
        tool_call_id = _tool_call_id_from_block(block)
        if not tool_call_id:
            return None
        tool_name = _tool_name_from_block(block) or "tool"
        if block.get("is_error") is True:
            event = {
                _KIND_KEY: _TOOL_ERROR_EVENT_KIND,
                "toolCallId": tool_call_id,
                "name": tool_name,
                "error": _tool_error_from_block(block),
            }
        else:
            event = {
                _KIND_KEY: _TOOL_RESULT_EVENT_KIND,
                "toolCallId": tool_call_id,
                "name": tool_name,
                "result": _tool_result_from_block(block),
            }
        _add_tool_summary(event, block)
        return event

    return None


def _is_tool_call_type(block_type: str) -> bool:
    return block_type in {"tool_use", "server_tool_use", "tool_call", "function_call"}


def _is_tool_result_type(block_type: str) -> bool:
    return block_type in {"tool_result", "tool_result_delta", "function_result"}


def _tool_call_id_from_block(block: dict[str, Any]) -> str | None:
    return _first_string_from_paths(block, ("toolCallId", "tool_call_id", "tool_use_id", "call_id", "id"))


def _tool_name_from_block(block: dict[str, Any]) -> str | None:
    return _first_string_from_paths(block, ("name", "tool_name", "toolName", "function.name"))


def _tool_args_from_block(block: dict[str, Any]) -> dict[str, Any]:
    args = _first_dict_from_paths(block, ("args", "arguments", "input", "function.arguments"))
    if args is not None:
        return args

    args_text = _first_string_from_paths(block, ("args", "arguments", "input", "function.arguments"))
    if not args_text:
        return {}
    try:
        parsed_args = json.loads(args_text)
    except json.JSONDecodeError:
        return {}
    return parsed_args if isinstance(parsed_args, dict) else {}


def _tool_result_from_block(block: dict[str, Any]) -> dict[str, Any]:
    for path in ("result", "content", "text"):
        result = _nested_value(block, path)
        if isinstance(result, dict):
            return result
        if result is not None:
            return {"content": result}
    return {}


def _tool_error_from_block(block: dict[str, Any]) -> str:
    error = _first_string_from_paths(block, ("error", "message", "content", "text"))
    if error:
        return error

    content = _nested_value(block, "content")
    if content is None:
        return "Tool failed."
    try:
        return json.dumps(content)
    except TypeError:
        return str(content)


def _add_tool_summary(event: dict[str, Any], block: dict[str, Any]) -> None:
    summary = _summary_from_value(block)
    if summary:
        event["summary"] = summary


def _get_local_agent(local_agent_name: str) -> _LocalAgent:
    local_agent = _LOCAL_AGENTS.get(local_agent_name)
    if local_agent is None:
        raise _LocalAgentSetupError(f"Unknown local agent: {local_agent_name}.")
    return local_agent


def _local_agent_command_not_found_message(local_agent: _LocalAgent) -> str:
    return f"Local agent command not found: {local_agent.executable()}."


def _confirm_local_agent_install(local_agent: _LocalAgent) -> bool:
    if not sys.stdin.isatty():
        raise _LocalAgentSetupError(
            f"Cannot prompt to install {local_agent.display_name} because stdin is not interactive."
        )
    response = input(
        f"Install {local_agent.display_name} now?\n\n"
        f"  {local_agent.install_command.current.display}\n\n"
        "Proceed? [y/N] "
    )
    return response.strip().lower() in {"y", "yes"}


def _install_local_agent(local_agent: _LocalAgent, install: AgentInstallPolicy) -> None:
    install_command = local_agent.install_command.current
    if install == "prompt" and not _confirm_local_agent_install(local_agent):
        raise _LocalAgentSetupError(f"{local_agent.display_name} was not installed.")

    print(f"Installing {local_agent.display_name}...", flush=True)
    try:
        subprocess.run(install_command.command, check=True)
    except FileNotFoundError:
        raise _LocalAgentSetupError(
            f"Could not install {local_agent.display_name}: {install_command.command[0]} was not found."
        ) from None
    except subprocess.CalledProcessError:
        raise _LocalAgentSetupError(
            f"Failed to install {local_agent.display_name} with:\n\n  {install_command.display}"
        ) from None


def _validate_local_agent_available(local_agent_name: str, install: AgentInstallPolicy) -> None:
    local_agent = _get_local_agent(local_agent_name)
    if local_agent.is_available():
        return
    if install == "never":
        raise _LocalAgentSetupError(_local_agent_command_not_found_message(local_agent))

    _install_local_agent(local_agent, install)
    if not local_agent.is_available():
        raise _LocalAgentSetupError(
            f"Installed {local_agent.display_name}, but {local_agent.executable()} is still not on PATH."
        )


async def _run_local_agent(
    local_agent_name: str, prompt: str, message_id: str, emit_event: _LocalEventSender
) -> tuple[bool, str]:
    local_agent = _get_local_agent(local_agent_name)
    session_key = (local_agent_name, message_id)
    success, message, session_id = await local_agent.run(prompt, _LOCAL_AGENT_SESSION_IDS.get(session_key), emit_event)
    if success and session_id is not None:
        _LOCAL_AGENT_SESSION_IDS[session_key] = session_id
    return success, message


def _make_event_payload(work: dict[str, Any], sequence: int, event: dict[str, Any]) -> dict[str, Any]:
    return {
        _TYPE_KEY: _EVENT_TYPE,
        _MESSAGE_ID_KEY: work[_MESSAGE_ID_KEY],
        _SEQUENCE_KEY: sequence,
        _EVENT_KEY: event,
    }


class _StreamEventAssembler:
    def __init__(self) -> None:
        self.message_id = ""
        self.text_by_index: dict[int, str] = {}

    def events_from_stream_event(self, value: dict[str, Any]) -> list[dict[str, Any]]:
        inner = _nested_value(value, _EVENT_KEY)
        if not isinstance(inner, dict):
            return []

        event_type = _nested_string(inner, _TYPE_KEY)
        if event_type == _MESSAGE_START_EVENT_TYPE:
            self.message_id = _first_string_from_paths(inner, ("message.id", "id")) or self.message_id
            self.text_by_index.clear()
            return []

        if event_type != _CONTENT_BLOCK_DELTA_EVENT_TYPE:
            return []

        index = inner.get("index")
        delta = _nested_value(inner, "delta")
        if not isinstance(index, int) or isinstance(index, bool) or not isinstance(delta, dict):
            return []
        if _nested_string(delta, _TYPE_KEY) != _TEXT_DELTA_DELTA_TYPE:
            return []

        text = _nested_string(delta, "text")
        if not text:
            return []

        accumulated_text = self.text_by_index.get(index, "") + text
        self.text_by_index[index] = accumulated_text
        block = {_TYPE_KEY: "text", "text": accumulated_text}
        event = _event_from_content_block(block)
        if event is None:
            return []
        event[_EVENT_SOURCE_KEY] = _content_block_source(self.message_id, "message.content", index, block)
        return [event]


class _StreamEventState:
    def __init__(self, *, deduplicate_cumulative_events: bool = False) -> None:
        self.deduplicate_cumulative_events = deduplicate_cumulative_events
        self.has_streamed_text = False
        self.text_by_source: dict[str, str] = {}
        self.seen_tool_event_keys: set[tuple[str, str]] = set()
        self.seen_thinking_events: set[tuple[str, str]] = set()
        self.tool_names_by_id: dict[str, str] = {}

    def prepare(self, event: dict[str, Any]) -> dict[str, Any] | None:
        event = dict(event)
        kind = event.get(_KIND_KEY)
        if kind == _TEXT_DELTA_EVENT_KIND:
            return self._prepare_text_event(event)
        if kind == _THINKING_EVENT_KIND:
            return self._prepare_thinking_event(event)
        if kind in {_TOOL_CALL_EVENT_KIND, _TOOL_RESULT_EVENT_KIND, _TOOL_ERROR_EVENT_KIND}:
            return self._prepare_tool_event(event)
        return _strip_internal_event_keys(event)

    def _prepare_text_event(self, event: dict[str, Any]) -> dict[str, Any] | None:
        text = event.get("text")
        if not isinstance(text, str) or not text:
            return None

        source = event.pop(_EVENT_SOURCE_KEY, _DEFAULT_TEXT_EVENT_SOURCE)
        if not isinstance(source, str) or not source:
            source = _DEFAULT_TEXT_EVENT_SOURCE
        if not self.deduplicate_cumulative_events:
            self.has_streamed_text = True
            return _strip_internal_event_keys(event)

        previous_text = self.text_by_source.get(source, "")
        if text.startswith(previous_text):
            delta = text[len(previous_text) :]
            self.text_by_source[source] = text
        elif previous_text.startswith(text):
            delta = ""
        else:
            overlap_length = _suffix_prefix_overlap_length(previous_text, text)
            delta = text[overlap_length:]
            self.text_by_source[source] = previous_text + delta

        if not delta:
            return None
        event["text"] = delta
        self.has_streamed_text = True
        return _strip_internal_event_keys(event)

    def _prepare_thinking_event(self, event: dict[str, Any]) -> dict[str, Any] | None:
        source = event.pop(_EVENT_SOURCE_KEY, "")
        detail = event.get("detail")
        if not isinstance(detail, str) or not detail:
            return None
        if not self.deduplicate_cumulative_events:
            return _strip_internal_event_keys(event)
        key = (source if isinstance(source, str) else "", detail)
        if key in self.seen_thinking_events:
            return None
        self.seen_thinking_events.add(key)
        return _strip_internal_event_keys(event)

    def _prepare_tool_event(self, event: dict[str, Any]) -> dict[str, Any] | None:
        kind = event.get(_KIND_KEY)
        tool_call_id = event.get("toolCallId")
        tool_name = event.get("name")
        if not isinstance(kind, str) or not isinstance(tool_call_id, str):
            return None

        if kind == _TOOL_CALL_EVENT_KIND and isinstance(tool_name, str):
            self.tool_names_by_id[tool_call_id] = tool_name
        elif event.get("name") == "tool" and tool_call_id in self.tool_names_by_id:
            event["name"] = self.tool_names_by_id[tool_call_id]

        if not self.deduplicate_cumulative_events:
            return _strip_internal_event_keys(event)

        key = (kind, tool_call_id)
        if key in self.seen_tool_event_keys:
            return None
        self.seen_tool_event_keys.add(key)
        return _strip_internal_event_keys(event)


def _strip_internal_event_keys(event: dict[str, Any]) -> dict[str, Any]:
    if _EVENT_SOURCE_KEY not in event:
        return event
    return {key: value for key, value in event.items() if key != _EVENT_SOURCE_KEY}


def _suffix_prefix_overlap_length(previous_text: str, text: str) -> int:
    max_overlap_length = min(len(previous_text), len(text))
    for overlap_length in range(max_overlap_length, 0, -1):
        if previous_text.endswith(text[:overlap_length]):
            return overlap_length
    return 0


class _TerminalEventPrinter:
    def __init__(self, quiet: bool) -> None:
        self.quiet = quiet
        self.has_streamed_text = False
        self.text_block_active = False
        self.last_print_was_text = False

    def print_event(self, event: dict[str, Any]) -> None:
        if self.quiet:
            return

        kind = event.get(_KIND_KEY)
        if kind == _TEXT_DELTA_EVENT_KIND:
            text = event.get("text")
            if not isinstance(text, str) or not text:
                return
            if not self.text_block_active:
                print("\nAssistant: ", end="", flush=True)
            print(text, end="", flush=True)
            self.has_streamed_text = True
            self.text_block_active = True
            self.last_print_was_text = True
            return

        if kind == _THINKING_EVENT_KIND:
            label = _terminal_event_detail(event, ("summary", "detail"))
            self._print_line("Thinking", label)
            return

        if kind == _TOOL_CALL_EVENT_KIND:
            self._print_line("Tool call", _terminal_tool_label(event))
            return

        if kind == _TOOL_RESULT_EVENT_KIND:
            self._print_line("Tool result", _terminal_tool_label(event))
            return

        if kind == _TOOL_ERROR_EVENT_KIND:
            label = _terminal_tool_label(event)
            error = _terminal_event_detail(event, ("error",))
            self._print_line("Tool error", f"{label}: {error}" if error else label)

    def finish(self, message: str) -> None:
        if self.quiet:
            return
        if self.has_streamed_text:
            print("", flush=True)
        else:
            print(f"\nAssistant: {message}", flush=True)

    def _print_line(self, title: str, detail: str) -> None:
        if self.last_print_was_text:
            print("", flush=True)
        print(f"\n{title}: {detail}" if detail else f"\n{title}", flush=True)
        self.text_block_active = False
        self.last_print_was_text = False


def _terminal_event_detail(event: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = event.get(key)
        if isinstance(value, str) and value:
            return _preview_text(value)
    return ""


def _terminal_tool_label(event: dict[str, Any]) -> str:
    name = event.get("name")
    return name if isinstance(name, str) and name else "tool"


def _preview_text(text: str, max_length: int = 240) -> str:
    compact_text = " ".join(text.split())
    if len(compact_text) <= max_length:
        return compact_text
    return f"{compact_text[: max_length - 3]}..."


async def _handle_work(websocket: Any, work: dict[str, Any], quiet: bool) -> None:
    if not quiet:
        print(f"\nUser: {work[_PROMPT_KEY]}", flush=True)

    sequence = 0
    terminal_printer = _TerminalEventPrinter(quiet)

    async def emit_event(event: dict[str, Any]) -> None:
        nonlocal sequence
        sequence += 1
        await websocket.send(json.dumps(_make_event_payload(work, sequence, event)))
        terminal_printer.print_event(event)

    success, message = await _run_local_agent(
        work[_LOCAL_AGENT_KEY], work[_PROMPT_KEY], work[_MESSAGE_ID_KEY], emit_event
    )
    terminal_printer.finish(message)
    await emit_event({_KIND_KEY: _DONE_EVENT_KIND, _SUCCESS_KEY: success, _MESSAGE_KEY: message})


async def _wait_for_stdin_eof() -> None:
    loop = asyncio.get_running_loop()
    future: asyncio.Future[None] = loop.create_future()

    def _on_stdin_ready() -> None:
        if sys.stdin.readline() == "" and not future.done():
            future.set_result(None)

    try:
        stdin_fileno = sys.stdin.fileno()
        loop.add_reader(stdin_fileno, _on_stdin_ready)
    except (AttributeError, NotImplementedError, OSError):
        await future
        return

    try:
        await future
    finally:
        loop.remove_reader(stdin_fileno)


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


async def _handle_messages(
    websocket: Any, quiet: bool, agent_id: str, base_url: str, install: AgentInstallPolicy
) -> bool:
    async for raw_message in websocket:
        message = json.loads(raw_message)
        message_type = message[_TYPE_KEY]
        if message_type == _START_TYPE:
            _validate_local_agent_available(message[_LOCAL_AGENT_KEY], install)
            _print_start_message(message, agent_id, base_url)
            continue
        if message_type == _UPDATE_TYPE:
            if _LOCAL_AGENT_KEY in message:
                _validate_local_agent_available(message[_LOCAL_AGENT_KEY], install)
            if _print_update(message):
                await websocket.close()
                return False
            continue
        if message_type != _WORK_TYPE:
            continue
        await _handle_work(websocket, message, quiet)
    return True


async def _run_until_closed_or_eof(
    websocket: Any, quiet: bool, install: AgentInstallPolicy, *, agent_id: str, base_url: str
) -> bool:
    messages_task = asyncio.create_task(_handle_messages(websocket, quiet, agent_id, base_url, install))
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


async def _connect_agent_async(
    agent_id: str,
    install: AgentInstallPolicy,
    *,
    base_url: str,
    headers: Mapping[str, str],
    quiet: bool,
) -> None:
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
                    if not await _run_until_closed_or_eof(
                        websocket, quiet, install, agent_id=agent_id, base_url=base_url
                    ):
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
