import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dart import agent_process
from dart.cli_command import CLI_COMMAND_ENVVAR, DEFAULT_CLI_COMMAND


class BackgroundAgentConnectionTests(unittest.TestCase):
    def test_write_registry_uses_sibling_state_dir_when_config_and_state_paths_collide(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "dart-tools"
            config_path.write_text("{}", encoding="UTF-8")
            registry_path = config_path.with_name("dart-tools-state") / "agent-connections.json"

            with (
                patch("dart.agent_process.platformdirs.user_config_path", return_value=config_path),
                patch("dart.agent_process.platformdirs.user_state_path", return_value=config_path),
            ):
                agent_process._write_registry({})

            self.assertEqual(config_path.read_text(encoding="UTF-8"), "{}")
            self.assertTrue(registry_path.is_file())

    def test_registry_path_uses_state_path_when_it_does_not_collide_with_config_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_path = Path(tmp_dir) / "state" / "dart-tools"
            config_path = Path(tmp_dir) / "config" / "dart-tools"

            with (
                patch("dart.agent_process.platformdirs.user_config_path", return_value=config_path),
                patch("dart.agent_process.platformdirs.user_state_path", return_value=state_path),
            ):
                self.assertEqual(agent_process._registry_path(), state_path / "agent-connections.json")

    def test_start_background_agent_connection_returns_existing_live_connection(self) -> None:
        connection = {
            "agentId": "agent-1",
            "pid": 1234,
            "startedAt": 1.0,
            "logPath": "/tmp/agent-1.log",
        }

        with (
            patch("dart.agent_process._load_pruned_registry", return_value={"agent-1": connection}),
            patch("dart.agent_process.subprocess.Popen") as popen_mock,
        ):
            result = agent_process.start_background_agent_connection(DEFAULT_CLI_COMMAND, "agent-1", "never")

        self.assertIs(result, connection)
        popen_mock.assert_not_called()

    def test_start_background_agent_connection_terminates_process_when_registry_write_fails(self) -> None:
        class FakeProcess:
            pid = 1234

            def poll(self):
                return None

        fake_process = FakeProcess()

        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "agent.log"
            with (
                patch("dart.agent_process._load_pruned_registry", return_value={}),
                patch("dart.agent_process._make_log_path", return_value=log_path),
                patch("dart.agent_process.subprocess.Popen", return_value=fake_process),
                patch("dart.agent_process.time.sleep"),
                patch("dart.agent_process.time.time", return_value=1.0),
                patch("dart.agent_process._write_registry", side_effect=OSError("cannot write")),
                patch("dart.agent_process._terminate_process") as terminate_process_mock,
            ):
                with self.assertRaisesRegex(agent_process.AgentConnectionError, "Could not register"):
                    agent_process.start_background_agent_connection(DEFAULT_CLI_COMMAND, "agent-1", "never")

        terminate_process_mock.assert_called_once_with(fake_process.pid)

    def test_start_background_agent_connection_runs_child_in_foreground_mode(self) -> None:
        class FakeProcess:
            pid = 1234

            def poll(self):
                return None

        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "agent.log"
            with (
                patch("dart.agent_process._load_pruned_registry", return_value={}),
                patch("dart.agent_process._make_log_path", return_value=log_path),
                patch("dart.agent_process.subprocess.Popen", return_value=FakeProcess()) as popen_mock,
                patch("dart.agent_process.time.sleep"),
                patch("dart.agent_process.time.time", return_value=1.0),
                patch("dart.agent_process._write_registry"),
            ):
                agent_process.start_background_agent_connection(DEFAULT_CLI_COMMAND, "agent-1", "never")

        command = popen_mock.call_args.args[0]
        self.assertIn("--quiet", command)
        self.assertIn("--foreground", command)
        self.assertIn("--install", command)
        self.assertIn("never", command)

    def test_start_background_agent_connection_passes_install_policy_to_child(self) -> None:
        class FakeProcess:
            pid = 1234

            def poll(self):
                return None

        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "agent.log"
            with (
                patch("dart.agent_process._load_pruned_registry", return_value={}),
                patch("dart.agent_process._make_log_path", return_value=log_path),
                patch("dart.agent_process.subprocess.Popen", return_value=FakeProcess()) as popen_mock,
                patch("dart.agent_process.time.sleep"),
                patch("dart.agent_process.time.time", return_value=1.0),
                patch("dart.agent_process._write_registry"),
            ):
                agent_process.start_background_agent_connection(DEFAULT_CLI_COMMAND, "agent-1", "auto")

        command = popen_mock.call_args.args[0]
        self.assertEqual(command[-2:], ["--install", "auto"])

    def test_start_background_agent_connection_reuses_cli_command_when_available(self) -> None:
        class FakeProcess:
            pid = 1234

            def poll(self):
                return None

        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "agent.log"
            with (
                patch("dart.agent_process._load_pruned_registry", return_value={}),
                patch("dart.agent_process._make_log_path", return_value=log_path),
                patch("dart.agent_process.shutil.which", return_value="/usr/local/bin/dartai"),
                patch("dart.agent_process.subprocess.Popen", return_value=FakeProcess()) as popen_mock,
                patch("dart.agent_process.time.sleep"),
                patch("dart.agent_process.time.time", return_value=1.0),
                patch("dart.agent_process._write_registry"),
            ):
                agent_process.start_background_agent_connection("dartai", "agent-1", "never")

        command = popen_mock.call_args.args[0]
        self.assertEqual(command[:3], ["dartai", "agent-connect", "agent-1"])
        self.assertEqual(popen_mock.call_args.kwargs["env"][CLI_COMMAND_ENVVAR], "dartai")


if __name__ == "__main__":
    unittest.main()
