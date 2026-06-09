import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dart import dart as dart_cli


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


if __name__ == "__main__":
    unittest.main()
