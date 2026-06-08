from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import platformdirs

_APP = "dart-tools"
_CONNECTIONS_KEY = "connections"
_AGENT_ID_KEY = "agentId"
_PID_KEY = "pid"
_STARTED_AT_KEY = "startedAt"
_LOG_PATH_KEY = "logPath"
_STOP_TIMEOUT_SECONDS = 5


class AgentConnectionError(Exception):
    pass


def start_background_agent_connection(agent_id: str) -> dict[str, Any]:
    registry = _load_pruned_registry()
    if agent_id in registry:
        raise AgentConnectionError(f"Agent {agent_id} already has a background connection.")

    log_path = _make_log_path(agent_id)
    command = [sys.executable, "-c", "from dart import cli; cli()", "agent-connect", agent_id, "--quiet"]
    with open(log_path, "ab") as log_file:
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
            start_new_session=os.name != "nt",
        )

    time.sleep(0.2)
    if process.poll() is not None:
        raise AgentConnectionError(f"Could not start background agent connection. Log: {log_path}")

    connection = {
        _AGENT_ID_KEY: agent_id,
        _PID_KEY: process.pid,
        _STARTED_AT_KEY: time.time(),
        _LOG_PATH_KEY: str(log_path),
    }
    registry[agent_id] = connection
    try:
        _write_registry(registry)
    except Exception as ex:
        _terminate_process(process.pid)
        raise AgentConnectionError(f"Could not register background agent connection. Log: {log_path}") from ex
    return connection


def list_background_agent_connections() -> list[dict[str, Any]]:
    registry = _load_pruned_registry()
    return sorted(registry.values(), key=lambda item: item[_STARTED_AT_KEY])


def disconnect_background_agent_connections(
    agent_id: str | None = None, *, all_connections: bool = False
) -> list[dict[str, Any]]:
    if not all_connections and agent_id is None:
        raise AgentConnectionError("Pass an agent ID or --all.")

    registry = _load_pruned_registry()
    if all_connections:
        matches = list(registry.values())
    else:
        matches = [registry[agent_id]] if agent_id in registry else []

    if not matches:
        target = "all agents" if all_connections else f"agent {agent_id}"
        raise AgentConnectionError(f"No background connections found for {target}.")

    stopped = []
    for connection in matches:
        _terminate_process(connection[_PID_KEY])
        registry.pop(connection[_AGENT_ID_KEY], None)
        stopped.append(connection)

    _write_registry(registry)
    return stopped


def _load_pruned_registry() -> dict[str, dict[str, Any]]:
    registry = _load_registry()
    pruned_registry = {key: value for key, value in registry.items() if _pid_exists(value.get(_PID_KEY))}
    if pruned_registry != registry:
        _write_registry(pruned_registry)
    return pruned_registry


def _load_registry() -> dict[str, dict[str, Any]]:
    registry_path = _registry_path()
    if not registry_path.is_file():
        return {}
    try:
        with open(registry_path, "r", encoding="UTF-8") as registry_file:
            content = json.load(registry_file)
    except (OSError, json.JSONDecodeError):
        return {}

    connections = content.get(_CONNECTIONS_KEY)
    if not isinstance(connections, dict):
        return {}

    return {
        value[_AGENT_ID_KEY]: value
        for value in connections.values()
        if isinstance(value, dict)
        and isinstance(value.get(_AGENT_ID_KEY), str)
        and isinstance(value.get(_PID_KEY), int)
        and isinstance(value.get(_STARTED_AT_KEY), (int, float))
        and isinstance(value.get(_LOG_PATH_KEY), str)
    }


def _write_registry(registry: dict[str, dict[str, Any]]) -> None:
    registry_path = _registry_path()
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = registry_path.with_suffix(".tmp")
    with open(temp_path, "w", encoding="UTF-8") as registry_file:
        json.dump({_CONNECTIONS_KEY: registry}, registry_file, indent=2)
    os.replace(temp_path, registry_path)


def _terminate_process(pid: int) -> None:
    if not _pid_exists(pid):
        return

    _signal_process(pid, signal.SIGTERM)
    deadline = time.monotonic() + _STOP_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if not _pid_exists(pid):
            return
        time.sleep(0.1)

    _signal_process(pid, getattr(signal, "SIGKILL", signal.SIGTERM))


def _signal_process(pid: int, sig: int) -> None:
    try:
        if os.name != "nt" and hasattr(os, "killpg"):
            os.killpg(pid, sig)
        else:
            os.kill(pid, sig)
    except ProcessLookupError:
        return


def _pid_exists(pid: Any) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _registry_path() -> Path:
    state_path = platformdirs.user_state_path(_APP)
    config_path = platformdirs.user_config_path(_APP)
    if state_path == config_path or (state_path.exists() and not state_path.is_dir()):
        state_path = state_path.with_name(f"{state_path.name}-state")
    return state_path / "agent-connections.json"


def _make_log_path(agent_id: str) -> Path:
    logs_dir = platformdirs.user_log_path(_APP) / "agent-connections"
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    return logs_dir / f"{agent_id}-{timestamp}.log"
