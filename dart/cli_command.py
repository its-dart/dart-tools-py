from __future__ import annotations

import os
import sys
from collections.abc import Mapping, Sequence

DEFAULT_CLI_COMMAND = "dart"
CLI_COMMAND_ENVVAR = "DART_CLI_COMMAND"


def get_invoked_cli_command(
    argv: Sequence[str] | None = None,
    environ: Mapping[str, str] | None = None,
) -> str:
    environ = os.environ if environ is None else environ
    command = environ.get(CLI_COMMAND_ENVVAR)
    if command:
        return command

    argv = sys.argv if argv is None else argv
    if argv:
        command = argv[0]
        if command and command != "-c":
            return command

    return DEFAULT_CLI_COMMAND
