import io
import tempfile
import unittest
from http import HTTPStatus
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import httpx

from dart import dart as dart_cli
from dart import old as dart_old
from dart.generated.models import AuthenticatedUser, Me, TokenLoginRequest, TokenLoginResponse
from dart.generated.types import Response


def _response(status_code: HTTPStatus, parsed=None, content: bytes = b"{}"):
    return Response(status_code=status_code, content=content, headers={}, parsed=parsed)


class ConfigPathTests(unittest.TestCase):
    def test_config_path_moves_existing_legacy_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "dart-tools" / "config.json"
            legacy_config_path = Path(tmp_dir) / "legacy-dart-tools"
            legacy_config_path.write_text('{"authToken": "dsa_token"}', encoding="UTF-8")

            self.assertEqual(
                dart_cli._migrate_config_fpath(config_path, legacy_config_path),
                config_path,
            )
            self.assertEqual(config_path.read_text(encoding="UTF-8"), '{"authToken": "dsa_token"}')
            self.assertFalse(legacy_config_path.exists())

    def test_config_path_moves_existing_legacy_file_that_blocks_config_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "dart-tools" / "config.json"
            legacy_config_path = config_path.parent
            legacy_config_path.write_text('{"authToken": "dsa_token"}', encoding="UTF-8")

            self.assertEqual(
                dart_cli._migrate_config_fpath(config_path, legacy_config_path),
                config_path,
            )
            self.assertEqual(config_path.read_text(encoding="UTF-8"), '{"authToken": "dsa_token"}')
            self.assertTrue(legacy_config_path.is_dir())

    def test_config_path_prefers_existing_config_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "dart-tools" / "config.json"
            legacy_config_path = Path(tmp_dir) / "legacy-dart-tools"
            config_path.parent.mkdir(parents=True)
            legacy_config_path.write_text('{"authToken": "legacy_token"}', encoding="UTF-8")
            config_path.write_text('{"authToken": "current_token"}', encoding="UTF-8")

            self.assertEqual(
                dart_cli._migrate_config_fpath(config_path, legacy_config_path),
                config_path,
            )
            self.assertEqual(config_path.read_text(encoding="UTF-8"), '{"authToken": "current_token"}')
            self.assertTrue(legacy_config_path.exists())

    def test_config_path_uses_config_file_when_legacy_path_is_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "dart-tools" / "config.json"
            legacy_config_path = config_path.parent
            legacy_config_path.mkdir(parents=True)

            self.assertEqual(
                dart_cli._migrate_config_fpath(config_path, legacy_config_path),
                config_path,
            )


class LoginTests(unittest.TestCase):
    def test_login_persists_token_when_config_parent_does_not_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "AppData" / "Roaming" / "dart-tools" / "dart-tools"

            self.assertFalse(config_path.parent.exists())
            with (
                patch("dart.dart._CONFIG_FPATH", config_path),
                patch("dart.dart.Dart.is_logged_in", side_effect=[False, True]),
            ):
                self.assertTrue(dart_cli.login("dsa_token"))
                self.assertEqual(dart_cli._Config().get(dart_cli._AUTH_TOKEN_KEY), "dsa_token")

    def test_login_fails_when_token_cannot_be_persisted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            blocked_parent = Path(tmp_dir) / "dart-tools"
            blocked_parent.write_text("", encoding="UTF-8")
            config_path = blocked_parent / "dart-tools"

            with (
                patch("dart.dart._CONFIG_FPATH", config_path),
                patch("dart.dart.Dart.is_logged_in", return_value=False),
            ):
                with self.assertRaises(dart_cli.DartException) as ctx:
                    dart_cli.login("dsa_token")

            self.assertEqual(
                str(ctx.exception),
                "Could not save your Dart config.\n\n"
                f"Config path: {config_path}\n\n"
                "Make sure the config path can be created and written, then try again. "
                "Alternatively, set the DART_TOKEN environment variable.",
            )

    def test_is_logged_in_uses_me_endpoint(self) -> None:
        dart = dart_cli.Dart()
        me = Me(
            is_logged_in=True,
            user=AuthenticatedUser(id="user-1", name="Test User", email="test@example.com"),
        )

        with (
            patch.object(dart, "_init_clients"),
            patch("dart.dart.api.get_me.sync", return_value=me) as get_me_mock,
        ):
            self.assertTrue(dart.is_logged_in())

        get_me_mock.assert_called_once_with(client=dart._public_api)

    def test_is_logged_in_returns_false_on_me_auth_failure(self) -> None:
        dart = dart_cli.Dart()

        with (
            patch.object(dart, "_init_clients"),
            patch("dart.dart.api.get_me.sync", return_value=None),
        ):
            self.assertFalse(dart.is_logged_in())

    def test_exchange_login_token_uses_generated_unauthenticated_token_login_endpoint(self) -> None:
        dart = dart_cli.Dart()
        public_api = Mock()
        response = _response(HTTPStatus.OK, parsed=TokenLoginResponse(auth_token="new_auth_token"))

        with (
            patch.object(dart, "_make_public_api_client", return_value=public_api) as make_client_mock,
            patch("dart.dart.api.token_login.sync_detailed", return_value=response) as token_login_mock,
        ):
            self.assertEqual(dart.exchange_login_token("login_token"), "new_auth_token")

        make_client_mock.assert_called_once_with(include_auth=False)
        token_login_mock.assert_called_once()
        self.assertIs(token_login_mock.call_args.kwargs["client"], public_api)
        body = token_login_mock.call_args.kwargs["body"]
        self.assertIsInstance(body, TokenLoginRequest)
        self.assertEqual(body.token, "login_token")

    def test_exchange_login_token_reports_invalid_token(self) -> None:
        dart = dart_cli.Dart()
        public_api = Mock()
        response = _response(HTTPStatus.UNAUTHORIZED, content=b'{"errors": ["Invalid token"]}')

        with (
            patch.object(dart, "_make_public_api_client", return_value=public_api),
            patch("dart.dart.api.token_login.sync_detailed", return_value=response),
            self.assertRaises(dart_cli.DartException) as ctx,
        ):
            dart.exchange_login_token("bad_login_token")

        self.assertEqual(str(ctx.exception), "Invalid token.")

    def test_token_login_persists_exchanged_auth_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "dart-tools" / "config.json"

            with (
                patch("dart.dart._CONFIG_FPATH", config_path),
                patch("dart.dart.Dart.exchange_login_token", return_value="new_auth_token") as exchange_mock,
            ):
                self.assertTrue(dart_cli.token_login("login_token"))

                exchange_mock.assert_called_once_with("login_token")
                self.assertEqual(dart_cli._Config().get(dart_cli._AUTH_TOKEN_KEY), "new_auth_token")

    def test_unauthenticated_headers_do_not_include_existing_auth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "dart-tools" / "config.json"

            with patch("dart.dart._CONFIG_FPATH", config_path):
                config = dart_cli._Config()
                config.set(dart_cli._AUTH_TOKEN_KEY, "existing_auth_token")
                dart = dart_cli.Dart(config=config)

                client = dart._make_public_api_client(include_auth=False)

        self.assertNotIn("Authorization", client._headers)

    def test_cli_authenticated_command_logs_in_and_continues(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "dart-tools" / "config.json"
            task = SimpleNamespace(title="New task", html_url="https://example.com/t/task-1", id="task-1")

            with (
                patch("dart.dart._CONFIG_FPATH", config_path),
                patch("dart.dart._is_cli", True),
                patch("dart.dart.Dart.is_logged_in", side_effect=[False, True]),
                patch("dart.dart.open_new_tab") as open_new_tab_mock,
                patch("builtins.input", return_value="new_token") as input_mock,
                patch("dart.dart._log"),
                patch("dart.dart.Dart.create_task", return_value=SimpleNamespace(item=task)) as create_task_mock,
            ):
                result = dart_cli.create_task("New task")

            self.assertIs(result, task)
            self.assertIn("new_token", config_path.read_text(encoding="UTF-8"))
            open_new_tab_mock.assert_called_once_with("https://app.dartai.com/?settings=account")
            input_mock.assert_called_once_with("Token: ")
            create_task_mock.assert_called_once()

    def test_cli_login_refreshes_client_headers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "dart-tools" / "config.json"

            with (
                patch("dart.dart._CONFIG_FPATH", config_path),
                patch("dart.dart._is_cli", True),
                patch("dart.dart.Dart.is_logged_in", side_effect=[False, True]),
                patch("dart.dart.open_new_tab"),
                patch("builtins.input", return_value="new_token"),
                patch("dart.dart._log"),
            ):
                dart = dart_cli.Dart()
                self.assertNotIn("Authorization", dart._public_api._headers)

                dart.ensure_logged_in_for_cli()

                self.assertEqual(dart._public_api._headers["Authorization"], "Bearer new_token")

    def test_public_api_auth_failure_logs_in_and_retries_once_for_cli(self) -> None:
        dart = dart_cli.Dart()
        body = object()
        parsed = object()

        with (
            patch("dart.dart._is_cli", True),
            patch.object(dart_cli.Dart, "_login_after_cli_auth_failure", autospec=True) as login_mock,
            patch(
                "dart.dart.api.create_task.sync_detailed",
                side_effect=[
                    _response(HTTPStatus.UNAUTHORIZED),
                    _response(HTTPStatus.OK, parsed=parsed),
                ],
            ) as sync_mock,
        ):
            result = dart.create_task(body)

        self.assertIs(result, parsed)
        login_mock.assert_called_once_with(dart)
        self.assertEqual(sync_mock.call_count, 2)

    def test_non_cli_auth_failure_keeps_explicit_auth_contract(self) -> None:
        dart = dart_cli.Dart()

        with (
            patch("dart.dart._is_cli", False),
            patch("dart.dart.open_new_tab") as open_new_tab_mock,
            patch("builtins.input") as input_mock,
            patch(
                "dart.dart.api.create_task.sync_detailed", return_value=_response(HTTPStatus.UNAUTHORIZED)
            ) as sync_mock,
        ):
            with self.assertRaises(dart_cli.DartException) as ctx:
                dart.create_task(object())

        self.assertIn("dart.login(token)", str(ctx.exception))
        sync_mock.assert_called_once()
        open_new_tab_mock.assert_not_called()
        input_mock.assert_not_called()

    def test_legacy_private_api_auth_failure_logs_in_and_retries_once_for_cli(self) -> None:
        dart = dart_old.DartOld()
        httpx_client = Mock()
        httpx_client.get.side_effect = [httpx.Response(401), httpx.Response(200)]
        dart._private_api = Mock()
        dart._private_api.get_httpx_client.return_value = httpx_client

        with (
            patch("dart.dart._is_cli", True),
            patch.object(dart_cli.Dart, "_login_after_cli_auth_failure", autospec=True) as login_mock,
        ):
            response = dart.get("/dartboards")

        self.assertEqual(response.status_code, 200)
        login_mock.assert_called_once_with(dart)
        self.assertEqual(httpx_client.get.call_count, 2)

    def test_background_agent_connection_ensures_auth_before_starting_process(self) -> None:
        events = []

        def ensure_logged_in(_dart):
            events.append("login")

        def start_background(_cli_command, agent_id):
            events.append("start")
            return {"agentId": agent_id, "startedAt": 1.0}

        with (
            patch.object(dart_cli.Dart, "ensure_logged_in_for_cli", ensure_logged_in),
            patch("dart.dart.start_background_agent_connection", side_effect=start_background),
        ):
            dart_cli.connect_agent("agent-1")

        self.assertEqual(events, ["login", "start"])

    def test_agent_connection_auth_failure_logs_in_and_retries_once_for_cli(self) -> None:
        events = []

        def connect_local_agent(*_args, **_kwargs):
            events.append("connect")
            if events.count("connect") == 1:
                raise dart_cli.AgentAuthError("Authentication failed")

        def login_after_auth_failure(_dart):
            events.append("login")

        with (
            patch("dart.dart._is_cli", True),
            patch.object(dart_cli.Dart, "ensure_logged_in_for_cli"),
            patch.object(dart_cli.Dart, "_login_after_cli_auth_failure", login_after_auth_failure),
            patch("dart.dart._connect_local_agent", side_effect=connect_local_agent),
        ):
            dart_cli.connect_agent("agent-1", background=False)

        self.assertEqual(events, ["connect", "login", "connect"])


class CliHostLogTests(unittest.TestCase):
    def test_cli_help_hides_internal_service_commands(self) -> None:
        stdout = io.StringIO()

        with (
            patch("sys.argv", ["dart", "--help"]),
            patch("dart.dart._start_version_check_thread", return_value=Mock()),
            patch("dart.dart._is_cli", False),
            patch("sys.stdout", stdout),
            self.assertRaises(SystemExit) as ctx,
        ):
            dart_cli.cli()

        self.assertEqual(ctx.exception.code, 0)
        help_text = stdout.getvalue()
        self.assertIn("login", help_text)
        self.assertNotIn("host-get", help_text)
        self.assertNotIn("host-set", help_text)
        self.assertNotIn("token-login", help_text)

    def test_cli_help_uses_invoked_command(self) -> None:
        stdout = io.StringIO()

        with (
            patch("sys.argv", ["dartai", "--help"]),
            patch("dart.dart._start_version_check_thread", return_value=Mock()),
            patch("dart.dart._is_cli", False),
            patch("sys.stdout", stdout),
            self.assertRaises(SystemExit) as ctx,
        ):
            dart_cli.cli()

        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("usage: dartai", stdout.getvalue())

    def test_cli_subcommand_help_uses_invoked_alias(self) -> None:
        stdout = io.StringIO()

        with (
            patch("sys.argv", ["dartai", "acc", "--help"]),
            patch("dart.dart._start_version_check_thread", return_value=Mock()),
            patch("dart.dart._is_cli", False),
            patch("sys.stdout", stdout),
            self.assertRaises(SystemExit) as ctx,
        ):
            dart_cli.cli()

        self.assertEqual(ctx.exception.code, 0)
        help_text = stdout.getvalue()
        self.assertIn("usage: dartai acc", help_text)
        self.assertNotIn("usage: dartai agent-connect", help_text)

    def test_auth_failure_message_uses_stored_cli_command(self) -> None:
        with (
            patch("dart.dart._is_cli", True),
            patch("dart.dart._cli_command", "dartai"),
            self.assertRaises(SystemExit) as ctx,
        ):
            dart_cli._auth_failure_exit()

        self.assertEqual(str(ctx.exception), "Not logged in, run\n\n  dartai login\n\nto log in.")

    def test_cli_logs_non_prod_host_before_command_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "dart-tools" / "config.json"
            messages = []

            with patch("dart.dart._CONFIG_FPATH", config_path):
                config = dart_cli._Config()
                config.host = dart_cli._STAG_HOST

                with (
                    patch("sys.argv", ["dart", "logout"]),
                    patch("dart.dart._start_version_check_thread", return_value=Mock()),
                    patch("dart.dart._print_pending_version_message"),
                    patch("dart.dart._log", side_effect=messages.append),
                    patch("dart.dart._is_cli", False),
                ):
                    dart_cli.cli()

        self.assertEqual(messages[0], "Host is stag")
        self.assertEqual(messages[1], "Already logged out.")

    def test_cli_skips_non_prod_host_log_for_host_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "dart-tools" / "config.json"
            messages = []

            with patch("dart.dart._CONFIG_FPATH", config_path):
                config = dart_cli._Config()
                config.host = dart_cli._STAG_HOST

                with (
                    patch("sys.argv", ["dart", "host-get"]),
                    patch("dart.dart._start_version_check_thread", return_value=Mock()),
                    patch("dart.dart._print_pending_version_message"),
                    patch("dart.dart._log", side_effect=messages.append),
                    patch("dart.dart._is_cli", False),
                ):
                    dart_cli.cli()

        self.assertEqual(messages, ["Host is stag", "Done."])


if __name__ == "__main__":
    unittest.main()
