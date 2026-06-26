from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from markdown_it import MarkdownIt
from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text


@dataclass
class _TerminalTurn:
    display_prompt: str
    user_name: str
    activity_rows: list[Text] = field(default_factory=list)
    assistant_text: str = ""
    failure_message: str = ""
    working_spinner: Spinner | None = None


class _ChatTranscript:
    def __init__(self, *, chat_key: str, title: str | None, console: Console) -> None:
        self.chat_key = chat_key
        self.title = title
        self.console = console
        self.items: list[_TerminalTurn | Text] = []
        self.live: Live | None = Live(self._render(), console=self.console, refresh_per_second=12)
        self.live.start()

    def append(self, item: _TerminalTurn | Text) -> None:
        self.items.append(item)
        self.update()

    def append_turn(self, display_prompt: str, user_name: str) -> _TerminalTurn:
        turn = _TerminalTurn(display_prompt=display_prompt, user_name=user_name)
        self.append(turn)
        return turn

    def update(self) -> None:
        if self.live is not None:
            self.live.update(self._render(), refresh=True)

    def close(self) -> None:
        if self.live is not None:
            self.live.stop()
            self.live = None
            self.console.print()

    def _render(self) -> Panel:
        rendered_items: list[Any] = []
        for index, item in enumerate(self.items):
            if index > 0:
                rendered_items.append(Text(""))
            if isinstance(item, Text):
                rendered_items.append(item)
            else:
                rendered_items.extend(_render_turn(item))

        return Panel(
            Group(*rendered_items),
            title=self.title or "Chat",
            title_align="left",
            border_style="dim",
            padding=(0, 1),
        )


class AgentUI:
    def __init__(self) -> None:
        self.console = Console()
        self.chat_titles_by_duid: dict[str, str] = {}
        self.active_chat_transcript: _ChatTranscript | None = None

    def activate_chat_transcript(self, chat_key: str, title: str | None) -> _ChatTranscript:
        if self.active_chat_transcript is not None and self.active_chat_transcript.chat_key == chat_key:
            self.active_chat_transcript.title = title or self.active_chat_transcript.title
            return self.active_chat_transcript

        self.close_active_chat_transcript()

        self.active_chat_transcript = _ChatTranscript(chat_key=chat_key, title=title, console=self.console)
        return self.active_chat_transcript

    def close_active_chat_transcript(self) -> None:
        if self.active_chat_transcript is not None:
            self.active_chat_transcript.close()
            self.active_chat_transcript = None

    def print_start_message(self, *, name: str, local_agent: str, agent_id: str, agent_url: str) -> None:
        self.console.print(
            Panel(
                Group(
                    Text(f"Local        {local_agent}", style="dim"),
                    Text(f"ID           {agent_id}", style="dim"),
                    Text(f"URL          {agent_url}", style="dim"),
                    Text(""),
                    Text(
                        "Stopping this process will disconnect the agent. "
                        "Rerun with --background to run in the background.",
                        style="dim",
                    ),
                ),
                title="Info",
                title_align="left",
                border_style="dim",
                padding=(0, 1),
            )
        )
        self.console.print(Text(f"• waiting for work from {name}", style="dim"))
        self.console.print()

    def print_update(self, title: str, changes: list[str]) -> None:
        self.close_active_chat_transcript()
        self.console.print()
        lines = [Text(title, style="default")]
        lines.extend(Text(change, style="dim") for change in changes)
        self.console.print(
            Panel(
                Group(*lines),
                title="Info",
                title_align="left",
                border_style="dim",
                padding=(0, 1),
            )
        )

    def print_status(self, symbol: str, message: str, style: str) -> None:
        self.close_active_chat_transcript()
        self.console.print(Text(f"{symbol} {message}", style=style))


class TerminalEventPrinter:
    def __init__(self, quiet: bool, ui: AgentUI) -> None:
        self.quiet = quiet
        self.ui = ui
        self.has_streamed_text = False
        self.transcript: _ChatTranscript | None = None
        self.turn: _TerminalTurn | None = None

    def start_turn(self, *, chat_key: str, chat_title: str | None, display_prompt: str, user_name: str) -> None:
        if self.quiet:
            return
        self.transcript = self.ui.activate_chat_transcript(chat_key, chat_title)
        self._append_chat_renamed_notice(chat_key, chat_title)
        self.turn = self.transcript.append_turn(display_prompt, user_name)

    def start_working(self, local_agent_name: str) -> None:
        if self.quiet or self.turn is None or self.transcript is None:
            return
        self.turn.working_spinner = Spinner("dots", text=f" {local_agent_name} working", style="dim")
        self.transcript.update()

    def append_text_delta(self, text: str) -> None:
        if self.quiet or self.turn is None or self.transcript is None or not text:
            return
        self.turn.assistant_text += text
        self.transcript.update()
        self.has_streamed_text = True

    def append_thinking(self, detail: str) -> None:
        self._add_activity("…", "thinking", detail, "dim")

    def append_tool_call(self, name: str, args: Any) -> None:
        label = _tool_call_label(name, args)
        self._add_activity("›", "tool", label, "dim")

    def append_tool_result(self) -> None:
        self._add_activity("·", "tool success", "", "dim")

    def append_tool_error(self, name: str, error: str) -> None:
        detail = f"{name}: {error}" if error else name
        self._add_activity("!", "tool error", detail, "red")

    def finish(self, message: str, *, success: bool) -> None:
        if self.quiet or self.turn is None or self.transcript is None:
            return
        self.turn.working_spinner = None
        if success and not self.has_streamed_text:
            self.turn.assistant_text = message
        if not success:
            self.turn.failure_message = message
        self.transcript.update()

    def _add_activity(self, symbol: str, label: str, detail: str, style: str) -> None:
        if self.turn is None or self.transcript is None:
            return
        line = Text(f"{symbol} {label}", style=style)
        if detail:
            line.append(f" {detail}", style=style)
        self.turn.activity_rows.append(line)
        self.transcript.update()

    def _append_chat_renamed_notice(self, chat_key: str, chat_title: str | None) -> None:
        if chat_title is None or self.transcript is None:
            return

        previous_title = self.ui.chat_titles_by_duid.get(chat_key)
        self.ui.chat_titles_by_duid[chat_key] = chat_title
        if previous_title is None or previous_title == chat_title:
            return

        self.transcript.append(Text(f"· chat renamed: {chat_title}", style="dim"))


def _render_turn(turn: _TerminalTurn) -> list[Any]:
    sections = [_turn_section(turn.user_name, _LocalMarkdown(turn.display_prompt), "magenta")]
    activity_rows = list(turn.activity_rows)
    if turn.working_spinner is not None:
        activity_rows.append(turn.working_spinner)
    if activity_rows:
        sections.append(_turn_section("ACTIVITY", Group(*activity_rows), "dim"))
    if turn.failure_message:
        sections.append(_turn_section("AGENT FAILED", _LocalMarkdown(turn.failure_message), "red"))
    elif turn.assistant_text:
        sections.append(_turn_section("AGENT", _LocalMarkdown(turn.assistant_text), "default"))
    return _join_turn_sections(sections)


def _turn_section(title: str, body: Any, style: str) -> Group:
    return Group(Text(title, style=f"bold {style}"), Padding(body, (0, 0, 0, 2)))


def _join_turn_sections(sections: list[Group]) -> list[Any]:
    joined: list[Any] = []
    for index, section in enumerate(sections):
        if index > 0:
            joined.append(Text(""))
        joined.append(section)
    return joined


class _LocalMarkdown(Markdown):
    def __init__(self, markup: str) -> None:
        super().__init__(markup)
        parser = MarkdownIt().enable("strikethrough").enable("table")
        parser.validateLink = lambda _url: True
        self.parsed = parser.parse(markup)


def _tool_call_label(name: str, args: Any) -> str:
    args_preview = _tool_args_preview(args)
    return f"{name} · {args_preview}" if args_preview else name


def _tool_args_preview(args: Any) -> str:
    if isinstance(args, dict):
        for key in ("command", "cmd", "query", "path", "file_path", "pattern"):
            value = args.get(key)
            if isinstance(value, str) and value:
                return _preview_text(value, 120)
        if args:
            return _preview_text(json.dumps(args, separators=(",", ":")), 120)
    if isinstance(args, str) and args:
        return _preview_text(args, 120)
    return ""


def _preview_text(text: str, max_length: int = 240) -> str:
    compact_text = " ".join(text.split())
    if len(compact_text) <= max_length:
        return compact_text
    return f"{compact_text[: max_length - 3]}..."
