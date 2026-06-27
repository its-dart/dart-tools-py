import asyncio
import io
import unittest
from unittest.mock import Mock, patch

from rich.console import Console

from dart import agent


class LocalAgentStreamingTests(unittest.IsolatedAsyncioTestCase):
    def test_claude_uses_stream_json_with_partial_messages(self) -> None:
        local_agent = agent._LOCAL_AGENTS["claude"]

        self.assertIn("stream-json", local_agent.start_command)
        self.assertIn("--include-partial-messages", local_agent.start_command)
        self.assertEqual(local_agent.output_mode, "jsonl")
        self.assertFalse(local_agent.stream_response_keys)
        self.assertTrue(local_agent.deduplicate_stream_events)
        self.assertTrue(local_agent.reassemble_stream_events)

    def test_cursor_uses_stream_json(self) -> None:
        local_agent = agent._LOCAL_AGENTS["cursor"]

        self.assertIn("stream-json", local_agent.start_command)
        self.assertIn("stream-json", local_agent.resume_command or ())
        self.assertEqual(local_agent.output_mode, "jsonl")
        self.assertFalse(local_agent.stream_response_keys)
        self.assertFalse(local_agent.deduplicate_stream_events)
        self.assertFalse(local_agent.reassemble_stream_events)

    def _prepare_claude_stream_events(self, values):
        local_agent = agent._LOCAL_AGENTS["claude"]
        stream_state = agent._StreamEventState(deduplicate_cumulative_events=True)
        stream_assembler = agent._StreamEventAssembler()
        events = []
        for value in values:
            for event in local_agent._events_from_value(value, stream_assembler):
                prepared_event = stream_state.prepare(event)
                if prepared_event is not None:
                    events.append(prepared_event)
        return events, stream_state

    def test_configured_agents_extract_text_delta_from_response_keys(self) -> None:
        cases = {
            "codex": ({"item": {"text": "codex text"}}, "codex text"),
            "copilot": (
                {"type": "assistant.message", "data": {"content": "copilot text", "phase": "final_answer"}},
                "copilot text",
            ),
            "gemini": ({"response": "gemini text"}, "gemini text"),
            "opencode": ({"part": {"text": "opencode text"}}, "opencode text"),
        }

        for name, (value, expected_text) in cases.items():
            with self.subTest(name=name):
                events = agent._LOCAL_AGENTS[name].events_from_value(value)
                self.assertEqual(events, [{"kind": "text_delta", "text": expected_text}])

    def test_local_agent_commands_include_permission_overrides(self) -> None:
        cases = {
            "claude": ("--dangerously-skip-permissions",),
            "codex": ("--dangerously-bypass-approvals-and-sandbox", "--skip-git-repo-check"),
            "copilot": ("--no-ask-user", "--allow-all"),
            "cursor": ("--force",),
            "gemini": ("--approval-mode", "yolo", "--skip-trust"),
            "opencode": ("--dangerously-skip-permissions",),
        }

        for name, expected_flags in cases.items():
            with self.subTest(name=name):
                local_agent = agent._LOCAL_AGENTS[name]
                command = local_agent.make_command(None, "prompt")
                self.assertTrue(all(flag in command for flag in expected_flags))
                if local_agent.resume_command is not None:
                    resume_command = local_agent.make_command("session-1", "prompt")
                    self.assertTrue(all(flag in resume_command for flag in expected_flags))

    def test_confirmed_json_failure_parsers_extract_concise_messages(self) -> None:
        claude_message = "Not logged in \u00b7 Please run /login"
        codex_message = (
            "unexpected status 401 Unauthorized: Missing bearer or basic authentication in header, "
            "url: https://api.openai.com/v1/responses"
        )
        gemini_message = (
            "Please set an Auth method in your /tmp/gemini/settings.json or specify one of the following "
            "environment variables before running: GEMINI_API_KEY, GOOGLE_GENAI_USE_VERTEXAI, "
            "GOOGLE_GENAI_USE_GCA"
        )
        opencode_message = "Unexpected server error. Check server logs for details."
        cases = {
            "claude": (
                ("result",),
                "\n".join(
                    [
                        agent.json.dumps({"type": "system", "subtype": "init", "apiKeySource": "none"}),
                        agent.json.dumps(
                            {
                                "type": "assistant",
                                "message": {"content": [{"type": "text", "text": claude_message}]},
                                "error": "authentication_failed",
                            }
                        ),
                        agent.json.dumps(
                            {"type": "result", "subtype": "success", "is_error": True, "result": claude_message}
                        ),
                    ]
                ),
                "",
                claude_message,
            ),
            "codex": (
                ("error.message",),
                "\n".join(
                    [
                        agent.json.dumps({"type": "thread.started", "thread_id": "thread-1"}),
                        agent.json.dumps({"type": "error", "message": "Reconnecting... 5/5"}),
                        agent.json.dumps({"type": "turn.failed", "error": {"message": codex_message}}),
                    ]
                ),
                "WARN failed to connect to websocket: HTTP error: 401 Unauthorized",
                codex_message,
            ),
            "gemini": (
                ("error.message",),
                agent.json.dumps(
                    {
                        "session_id": "session-1",
                        "error": {"type": "Error", "message": gemini_message, "code": 41},
                    }
                ),
                "YOLO mode is enabled. All tool calls will be automatically approved.",
                gemini_message,
            ),
            "opencode": (
                ("error.data.message",),
                agent.json.dumps(
                    {
                        "type": "error",
                        "timestamp": 1782530074868,
                        "sessionID": "ses_0f8ed97f6ffeMk8cmmE9D7DGt2",
                        "error": {
                            "name": "UnknownError",
                            "data": {"message": opencode_message, "ref": "err_96efda90"},
                        },
                    }
                ),
                "",
                opencode_message,
            ),
        }

        for name, (failure_paths, stdout, stderr, expected_message) in cases.items():
            with self.subTest(name=name):
                local_agent = agent._LOCAL_AGENTS[name]
                self.assertEqual(local_agent.failure_response_keys, failure_paths)
                self.assertEqual(local_agent.parse_failure_output(stdout, stderr), expected_message)

    def test_plain_non_json_failure_output_is_compacted_and_capped(self) -> None:
        copilot_output = "\n".join(
            [
                "Error: No authentication information found.",
                "",
                "Copilot can be authenticated with GitHub using an OAuth Token or a Fine-Grained Personal Access Token.",
                "",
                "To authenticate, you can use any of the following methods:",
                "  \u2022 Start 'copilot' and run the '/login' command",
                "  \u2022 Set the COPILOT_GITHUB_TOKEN, GH_TOKEN, or GITHUB_TOKEN environment variable",
                "  \u2022 Run 'gh auth login' to authenticate with the GitHub CLI",
            ]
        )
        cursor_output = (
            "Error: Authentication required. Please run 'agent login' first, or set CURSOR_API_KEY environment "
            "variable."
        )

        copilot_message = agent._LOCAL_AGENTS["copilot"].parse_failure_output("", copilot_output)
        cursor_message = agent._LOCAL_AGENTS["cursor"].parse_failure_output("", cursor_output)

        self.assertEqual(agent._LOCAL_AGENTS["copilot"].failure_response_keys, ())
        self.assertEqual(agent._LOCAL_AGENTS["cursor"].failure_response_keys, ())
        self.assertNotIn("\n", copilot_message)
        self.assertLessEqual(len(copilot_message), 300)
        self.assertTrue(copilot_message.startswith("Error: No authentication information found."))
        self.assertTrue(copilot_message.endswith("..."))
        self.assertEqual(cursor_message, cursor_output)

    def test_unknown_json_failure_output_uses_generic_message(self) -> None:
        cases = {
            "codex": (
                agent.json.dumps({"item": {"text": "normal response keys are not failure fields"}}),
                "Codex failed. Check the local agent logs for details.",
            ),
            "opencode": (
                agent.json.dumps({"type": "error", "message": "unconfirmed opencode error path"}),
                "OpenCode failed. Check the local agent logs for details.",
            ),
        }

        for name, (stdout, expected_message) in cases.items():
            with self.subTest(name=name):
                message = agent._LOCAL_AGENTS[name].parse_failure_output(stdout, "")
                self.assertEqual(message, expected_message)
                self.assertNotIn("{", message)
                self.assertNotIn("unconfirmed", message)
                self.assertNotIn("normal response", message)

    def test_unknown_json_failure_output_falls_back_to_plain_output(self) -> None:
        codex_stdout = agent.json.dumps({"type": "thread.started", "thread_id": "thread-1"})
        codex_stderr = "fatal: authentication required"
        cursor_stdout = "\n".join(
            [
                agent.json.dumps({"type": "system", "session_id": "session-1"}),
                "Authentication required. Please run 'agent login' first.",
            ]
        )

        self.assertEqual(agent._LOCAL_AGENTS["codex"].parse_failure_output(codex_stdout, codex_stderr), codex_stderr)
        self.assertEqual(
            agent._LOCAL_AGENTS["cursor"].parse_failure_output(cursor_stdout, ""),
            "Authentication required. Please run 'agent login' first.",
        )

    def test_attachment_request_headers_keep_auth_for_same_origin_urls(self) -> None:
        headers = {
            "Origin": "https://app.dartai.com",
            "Authorization": "Bearer secret",
            "client-duid": "client-1",
            "X-Test": "ok",
        }

        self.assertEqual(
            agent._make_attachment_request_headers(
                "https://app.dartai.com",
                "https://app.dartai.com/api/attachments/attachment-1",
                headers,
            ),
            {
                "Authorization": "Bearer secret",
                "client-duid": "client-1",
                "X-Test": "ok",
            },
        )

    def test_attachment_request_headers_strip_auth_for_off_origin_urls(self) -> None:
        headers = {
            "Origin": "https://app.dartai.com",
            "Authorization": "Bearer secret",
            "client-duid": "client-1",
            "X-Test": "ok",
        }

        self.assertEqual(
            agent._make_attachment_request_headers(
                "https://app.dartai.com",
                "https://files.example.test/attachment-1",
                headers,
            ),
            {"X-Test": "ok"},
        )

    def test_start_message_copy_includes_background_and_log_path(self) -> None:
        ui = agent.AgentUI()
        ui.console = Console(file=io.StringIO(), record=True, force_terminal=False, width=120)

        ui.print_start_message(
            name="Review agent",
            local_agent="codex",
            agent_id="agent-1",
            agent_url="https://dart.test/a/agent-1",
            log_path="/tmp/dart-agent.log",
        )

        output = ui.console.export_text()
        self.assertIn(
            "Stopping this process will disconnect the agent, rerun with --background to run in the background",
            output,
        )
        self.assertNotIn("run in the background.", output)
        self.assertIn("Writing logs to /tmp/dart-agent.log", output)

    def test_claude_terminal_result_is_not_streamed_as_text_delta(self) -> None:
        local_agent = agent._LOCAL_AGENTS["claude"]

        events = local_agent.events_from_value({"type": "result", "result": "final text", "session_id": "session-1"})
        message, session_id = local_agent.parse_output(
            '{"type":"result","result":"final text","session_id":"session-1"}',
            "",
        )

        self.assertEqual(events, [])
        self.assertEqual(message, "final text")
        self.assertEqual(session_id, "session-1")

    def test_cursor_terminal_result_is_not_streamed_as_text_delta(self) -> None:
        local_agent = agent._LOCAL_AGENTS["cursor"]

        events = local_agent.events_from_value({"type": "result", "result": "final text", "session_id": "session-1"})
        message, session_id = local_agent.parse_output(
            '{"type":"result","result":"final text","session_id":"session-1"}',
            "",
        )

        self.assertEqual(events, [])
        self.assertEqual(message, "final text")
        self.assertEqual(session_id, "session-1")

    def test_events_from_value_extracts_thinking_event(self) -> None:
        local_agent = agent._LOCAL_AGENTS["codex"]

        events = local_agent.events_from_value(
            {"type": "reasoning", "summary": "Plan", "item": {"content": "Think through the request."}}
        )

        self.assertEqual(
            events,
            [{"kind": "thinking", "detail": "Think through the request.", "summary": "Plan"}],
        )

    def test_events_from_value_extracts_claude_content_blocks(self) -> None:
        local_agent = agent._LOCAL_AGENTS["claude"]

        events = local_agent.events_from_value(
            {
                "type": "assistant",
                "message": {
                    "content": [
                        {"type": "thinking", "thinking": "Need to inspect files."},
                        {"type": "text", "text": "I will check that."},
                        {"type": "tool_use", "id": "toolu-1", "name": "Read", "input": {"file_path": "a.py"}},
                    ]
                },
            }
        )

        self.assertEqual(
            events,
            [
                {"kind": "thinking", "detail": "Need to inspect files."},
                {"kind": "text_delta", "text": "I will check that."},
                {
                    "kind": "tool_call",
                    "toolCallId": "toolu-1",
                    "name": "Read",
                    "args": {"file_path": "a.py"},
                },
            ],
        )

    def test_events_from_value_extracts_claude_tool_result_blocks(self) -> None:
        local_agent = agent._LOCAL_AGENTS["claude"]

        events = local_agent.events_from_value(
            {
                "type": "user",
                "message": {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "toolu-1",
                            "content": "file contents",
                        }
                    ]
                },
            }
        )

        self.assertEqual(
            events,
            [{"kind": "tool_result", "toolCallId": "toolu-1", "name": "tool", "result": {"content": "file contents"}}],
        )

    def test_claude_stream_events_reassemble_into_incremental_text(self) -> None:
        values = [
            {"type": "stream_event", "event": {"type": "message_start", "message": {"id": "msg-1"}}},
            {
                "type": "stream_event",
                "event": {
                    "type": "content_block_delta",
                    "index": 0,
                    "delta": {"type": "text_delta", "text": "Hi"},
                },
            },
            {
                "type": "stream_event",
                "event": {
                    "type": "content_block_delta",
                    "index": 0,
                    "delta": {"type": "text_delta", "text": "!"},
                },
            },
            {
                "type": "assistant",
                "message": {"content": [{"type": "text", "text": "Hi!"}]},
            },
            {"type": "result", "result": "Hi!", "session_id": "session-1"},
        ]

        events, stream_state = self._prepare_claude_stream_events(values)

        self.assertEqual(events, [{"kind": "text_delta", "text": "Hi"}, {"kind": "text_delta", "text": "!"}])
        self.assertTrue(stream_state.has_streamed_text)

    def test_claude_stream_with_tool_use_takes_args_from_snapshot(self) -> None:
        values = [
            {"type": "stream_event", "event": {"type": "message_start", "message": {"id": "msg-1"}}},
            {
                "type": "stream_event",
                "event": {
                    "type": "content_block_delta",
                    "index": 0,
                    "delta": {"type": "text_delta", "text": "I will "},
                },
            },
            {
                "type": "stream_event",
                "event": {
                    "type": "content_block_delta",
                    "index": 0,
                    "delta": {"type": "text_delta", "text": "read it."},
                },
            },
            {
                "type": "stream_event",
                "event": {
                    "type": "content_block_delta",
                    "index": 1,
                    "delta": {"type": "input_json_delta", "partial_json": '{"file_path":"a.py"}'},
                },
            },
            {
                "type": "assistant",
                "message": {
                    "id": "msg-1",
                    "content": [
                        {"type": "text", "text": "I will read it."},
                        {"type": "tool_use", "id": "toolu-1", "name": "Read", "input": {"file_path": "a.py"}},
                    ],
                },
            },
            {
                "type": "user",
                "message": {
                    "id": "msg-2",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "toolu-1",
                            "content": "file contents",
                        }
                    ],
                },
            },
        ]

        events, _stream_state = self._prepare_claude_stream_events(values)

        self.assertEqual(
            events,
            [
                {"kind": "text_delta", "text": "I will "},
                {"kind": "text_delta", "text": "read it."},
                {
                    "kind": "tool_call",
                    "toolCallId": "toolu-1",
                    "name": "Read",
                    "args": {"file_path": "a.py"},
                },
                {
                    "kind": "tool_result",
                    "toolCallId": "toolu-1",
                    "name": "Read",
                    "result": {"content": "file contents"},
                },
            ],
        )

    def test_claude_stream_multi_turn_resets_per_message(self) -> None:
        values = [
            {"type": "stream_event", "event": {"type": "message_start", "message": {"id": "msg-1"}}},
            {
                "type": "stream_event",
                "event": {
                    "type": "content_block_delta",
                    "index": 0,
                    "delta": {"type": "text_delta", "text": "Hi"},
                },
            },
            {"type": "stream_event", "event": {"type": "message_start", "message": {"id": "msg-2"}}},
            {
                "type": "stream_event",
                "event": {
                    "type": "content_block_delta",
                    "index": 0,
                    "delta": {"type": "text_delta", "text": "Again"},
                },
            },
        ]

        events, _stream_state = self._prepare_claude_stream_events(values)

        self.assertEqual(events, [{"kind": "text_delta", "text": "Hi"}, {"kind": "text_delta", "text": "Again"}])

    def test_stream_state_deduplicates_claude_partial_messages(self) -> None:
        local_agent = agent._LOCAL_AGENTS["claude"]
        stream_state = agent._StreamEventState(deduplicate_cumulative_events=True)
        values = [
            {
                "type": "assistant",
                "message": {"id": "msg-1", "content": [{"type": "text", "text": "Let me"}]},
            },
            {
                "type": "assistant",
                "message": {
                    "id": "msg-1",
                    "content": [
                        {"type": "text", "text": "Let me check the git log."},
                        {"type": "tool_use", "id": "toolu-1", "name": "Bash", "input": {"command": "git log"}},
                    ],
                },
            },
            {
                "type": "assistant",
                "message": {
                    "id": "msg-1",
                    "content": [
                        {"type": "text", "text": "Let me check the git log."},
                        {"type": "tool_use", "id": "toolu-1", "name": "Bash", "input": {"command": "git log"}},
                    ],
                },
            },
            {
                "type": "user",
                "message": {
                    "id": "msg-2",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "toolu-1",
                            "content": "commit output",
                        }
                    ],
                },
            },
            {
                "type": "user",
                "message": {
                    "id": "msg-2",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "toolu-1",
                            "content": "commit output",
                        }
                    ],
                },
            },
            {
                "type": "assistant",
                "message": {"id": "msg-3", "content": [{"type": "text", "text": "The commit was yesterday."}]},
            },
            {"type": "result", "result": "The commit was yesterday.", "session_id": "session-1"},
        ]

        events = []
        for value in values:
            for event in local_agent._events_from_value(value):
                prepared_event = stream_state.prepare(event)
                if prepared_event is not None:
                    events.append(prepared_event)

        self.assertEqual(
            events,
            [
                {"kind": "text_delta", "text": "Let me"},
                {"kind": "text_delta", "text": " check the git log."},
                {"kind": "tool_call", "toolCallId": "toolu-1", "name": "Bash", "args": {"command": "git log"}},
                {
                    "kind": "tool_result",
                    "toolCallId": "toolu-1",
                    "name": "Bash",
                    "result": {"content": "commit output"},
                },
                {"kind": "text_delta", "text": "The commit was yesterday."},
            ],
        )

    def test_stream_state_deduplicates_cumulative_text_without_message_ids_when_enabled(self) -> None:
        stream_state = agent._StreamEventState(deduplicate_cumulative_events=True)
        events = [
            {"kind": "text_delta", "text": "Let me check."},
            {"kind": "text_delta", "text": "The commit"},
            {"kind": "text_delta", "text": "The commit was yesterday."},
        ]

        prepared_events = [stream_state.prepare(event) for event in events]

        self.assertEqual(
            prepared_events,
            [
                {"kind": "text_delta", "text": "Let me check."},
                {"kind": "text_delta", "text": "The commit"},
                {"kind": "text_delta", "text": " was yesterday."},
            ],
        )

    def test_stream_state_keeps_repeated_text_when_deduplication_is_disabled(self) -> None:
        stream_state = agent._StreamEventState()
        events = [
            {"kind": "text_delta", "text": "foo"},
            {"kind": "text_delta", "text": "foo"},
            {"kind": "text_delta", "text": "The commit"},
            {"kind": "text_delta", "text": "The commit"},
        ]

        prepared_events = [stream_state.prepare(event) for event in events]

        self.assertEqual(prepared_events, events)

    def test_cursor_stream_json_text_and_tool_events_are_normalized(self) -> None:
        local_agent = agent._LOCAL_AGENTS["cursor"]

        text_events = local_agent.events_from_value(
            {
                "type": "assistant",
                "message": {"role": "assistant", "content": [{"type": "text", "text": "Cursor text"}]},
                "session_id": "session-1",
            }
        )
        call_events = local_agent.events_from_value(
            {
                "type": "tool_call",
                "subtype": "started",
                "call_id": "call-1",
                "tool_call": {
                    "tool": {"case": "shellToolCall", "value": {"args": {"command": "pwd"}}},
                },
                "session_id": "session-1",
            }
        )
        result_events = local_agent.events_from_value(
            {
                "type": "tool_call",
                "subtype": "completed",
                "call_id": "call-1",
                "tool_call": {
                    "tool": {
                        "case": "shellToolCall",
                        "value": {"result": {"result": {"case": "success", "value": {"exitCode": 0}}}},
                    },
                },
                "session_id": "session-1",
            }
        )

        self.assertEqual(text_events, [{"kind": "text_delta", "text": "Cursor text"}])
        self.assertEqual(
            call_events,
            [{"kind": "tool_call", "toolCallId": "call-1", "name": "Bash", "args": {"command": "pwd"}}],
        )
        self.assertEqual(
            result_events,
            [
                {
                    "kind": "tool_result",
                    "toolCallId": "call-1",
                    "name": "Bash",
                    "result": {"result": {"case": "success", "value": {"exitCode": 0}}},
                }
            ],
        )

    def test_cursor_user_text_content_is_not_streamed_as_assistant_text(self) -> None:
        local_agent = agent._LOCAL_AGENTS["cursor"]

        events = local_agent.events_from_value(
            {
                "type": "user",
                "message": {"role": "user", "content": [{"type": "text", "text": "User prompt"}]},
                "session_id": "session-1",
            }
        )

        self.assertEqual(events, [])

    def test_copilot_uses_only_final_answer_messages_as_response_text(self) -> None:
        local_agent = agent._LOCAL_AGENTS["copilot"]
        output = "\n".join(
            agent.json.dumps(value)
            for value in (
                {"type": "user.message", "data": {"content": "User prompt"}},
                {"type": "assistant.message", "data": {"content": "OK", "phase": "final_answer"}},
                {"type": "assistant.message", "data": {"content": "Finishing up.", "phase": "commentary"}},
                {"type": "session.task_complete", "data": {"summary": "Completed."}},
                {"type": "result", "sessionId": "session-1"},
            )
        )

        message, session_id = local_agent.parse_output(output, "")
        events = [
            event
            for value in agent._load_json_values(output, local_agent.output_mode)
            for event in local_agent.events_from_value(value)
        ]

        self.assertEqual(message, "OK")
        self.assertEqual(session_id, "session-1")
        self.assertEqual(events, [{"kind": "text_delta", "text": "OK"}])

    def test_copilot_tool_events_use_tool_call_id_from_data_payload(self) -> None:
        local_agent = agent._LOCAL_AGENTS["copilot"]
        stream_state = agent._StreamEventState()
        values = [
            {
                "type": "tool.execution_start",
                "id": "envelope-start",
                "data": {"toolCallId": "call-1", "toolName": "task_complete", "arguments": {"summary": "done"}},
            },
            {
                "type": "tool.execution_complete",
                "id": "envelope-complete",
                "data": {"toolCallId": "call-1", "result": {"content": "ok"}},
            },
        ]

        events = []
        for value in values:
            for event in local_agent._events_from_value(value):
                prepared_event = stream_state.prepare(event)
                if prepared_event is not None:
                    events.append(prepared_event)

        self.assertEqual(
            events,
            [
                {
                    "kind": "tool_call",
                    "toolCallId": "call-1",
                    "name": "task_complete",
                    "args": {"summary": "done"},
                },
                {
                    "kind": "tool_result",
                    "toolCallId": "call-1",
                    "name": "task_complete",
                    "result": {"content": "ok"},
                },
            ],
        )

    def test_events_from_value_extracts_tool_call_and_result_events(self) -> None:
        local_agent = agent._LOCAL_AGENTS["codex"]

        call_events = local_agent.events_from_value(
            {
                "type": "tool_call",
                "item": {"id": "call-1", "tool_name": "shell", "args": {"cmd": "pwd"}},
            }
        )
        result_events = local_agent.events_from_value(
            {
                "type": "tool_result",
                "item": {"id": "call-1", "tool_name": "shell", "result": {"stdout": "/tmp"}},
            }
        )

        self.assertEqual(
            call_events,
            [{"kind": "tool_call", "toolCallId": "call-1", "name": "shell", "args": {"cmd": "pwd"}}],
        )
        self.assertEqual(
            result_events,
            [{"kind": "tool_result", "toolCallId": "call-1", "name": "shell", "result": {"stdout": "/tmp"}}],
        )

    async def test_handle_work_sends_ordered_events_and_terminal_done(self) -> None:
        sent_payloads = []

        class Websocket:
            async def send(self, payload: str) -> None:
                sent_payloads.append(payload)

        async def fake_run_local_agent(
            local_agent_name, prompt, message_id, model, thinking_level, attachments, emit_event
        ):
            await emit_event({"kind": "text_delta", "text": "hello"})
            await emit_event({"kind": "thinking", "detail": "done thinking"})
            return True, "hello"

        work = {"type": "message", "id": "work-1", "localAgent": "codex", "prompt": "Say hello"}
        with patch("dart.agent._run_local_agent", new=fake_run_local_agent):
            await agent._handle_work(
                Websocket(), work, quiet=True, base_url="https://dart.test", headers={}, ui=agent.AgentUI()
            )

        parsed_payloads = [agent.json.loads(payload) for payload in sent_payloads]
        self.assertEqual([payload["sequence"] for payload in parsed_payloads], [1, 2, 3])
        self.assertEqual(parsed_payloads[0]["event"], {"kind": "text_delta", "text": "hello"})
        self.assertEqual(parsed_payloads[1]["event"], {"kind": "thinking", "detail": "done thinking"})
        self.assertEqual(parsed_payloads[2]["event"], {"kind": "done", "success": True, "message": "hello"})

    async def test_handle_work_prints_streamed_text_as_it_arrives(self) -> None:
        class Websocket:
            async def send(self, payload: str) -> None:
                pass

        async def fake_run_local_agent(
            local_agent_name, prompt, message_id, model, thinking_level, attachments, emit_event
        ):
            await emit_event({"kind": "text_delta", "text": "hello"})
            await emit_event({"kind": "tool_call", "toolCallId": "toolu-1", "name": "Read", "args": {}})
            await emit_event({"kind": "text_delta", "text": "again"})
            return True, "hello"

        class Printer:
            def __init__(self, quiet, ui) -> None:
                self.calls = []

            def start_turn(self, **kwargs) -> None:
                pass

            def start_working(self, local_agent_name) -> None:
                pass

            def append_text_delta(self, text) -> None:
                self.calls.append(("text", text))

            def append_tool_call(self, name, args) -> None:
                self.calls.append(("tool", name, args))

            def finish(self, message, *, success) -> None:
                self.calls.append(("finish", message, success))

        printer = Printer(False, agent.AgentUI())
        work = {"type": "message", "id": "work-1", "localAgent": "codex", "prompt": "Say hello"}
        with (
            patch("dart.agent._run_local_agent", new=fake_run_local_agent),
            patch("dart.agent.TerminalEventPrinter", return_value=printer),
        ):
            await agent._handle_work(
                Websocket(), work, quiet=False, base_url="https://dart.test", headers={}, ui=agent.AgentUI()
            )

        self.assertEqual(
            printer.calls,
            [
                ("text", "hello"),
                ("tool", "Read", {}),
                ("text", "again"),
                ("finish", "hello", True),
            ],
        )

    async def test_handle_messages_validates_local_agent_from_update(self) -> None:
        class Websocket:
            def __init__(self) -> None:
                self.messages = [
                    agent.json.dumps(
                        {
                            "type": "update",
                            "title": "Agent settings changed",
                            "changes": ["Local agent changed from Claude Code to Codex."],
                            "localAgent": "codex",
                        }
                    )
                ]

            def __aiter__(self):
                return self

            async def __anext__(self) -> str:
                if not self.messages:
                    raise StopAsyncIteration
                return self.messages.pop(0)

        setup_error = agent._LocalAgentSetupError("Local agent command not found: codex.")
        ui = agent.AgentUI()
        with (
            patch("dart.agent._validate_local_agent_available", side_effect=setup_error) as validate_mock,
            patch("dart.agent._print_update_message") as print_update_mock,
            self.assertRaises(agent._LocalAgentSetupError),
        ):
            await agent._handle_messages(Websocket(), True, "agent-1", "https://dart.test", {}, ui, "never")

        validate_mock.assert_called_once_with("codex", "never")
        print_update_mock.assert_not_called()

    async def test_handle_messages_passes_background_log_path_to_start_message(self) -> None:
        class Websocket:
            def __init__(self) -> None:
                self.messages = [
                    agent.json.dumps(
                        {
                            "type": "start",
                            "name": "Review agent",
                            "localAgent": "codex",
                        }
                    )
                ]

            def __aiter__(self):
                return self

            async def __anext__(self) -> str:
                if not self.messages:
                    raise StopAsyncIteration
                return self.messages.pop(0)

        ui = Mock()
        with (
            patch("dart.agent._validate_local_agent_available"),
            patch.dict("dart.agent.os.environ", {agent.AGENT_CONNECTION_LOG_PATH_ENVVAR: "/tmp/dart-agent.log"}),
        ):
            await agent._handle_messages(Websocket(), True, "agent-1", "https://dart.test", {}, ui, "never")

        ui.print_start_message.assert_called_once_with(
            name="Review agent",
            local_agent="codex",
            agent_id="agent-1",
            agent_url="https://dart.test/a/agent-1",
            log_path="/tmp/dart-agent.log",
        )

    def test_validate_local_agent_available_never_preserves_missing_command_error(self) -> None:
        with (
            patch("dart.agent.shutil.which", return_value=None),
            patch("dart.agent.subprocess.run") as run_mock,
            self.assertRaisesRegex(agent._LocalAgentSetupError, "Local agent command not found: codex\\."),
        ):
            agent._validate_local_agent_available("codex", "never")

        run_mock.assert_not_called()

    def test_validate_local_agent_available_auto_installs_and_rechecks_path(self) -> None:
        with (
            patch("dart.agent.shutil.which", side_effect=[None, "/usr/local/bin/codex"]),
            patch("dart.agent.subprocess.run") as run_mock,
            patch("builtins.print"),
        ):
            agent._validate_local_agent_available("codex", "auto")

        run_mock.assert_called_once_with(("npm", "install", "-g", "@openai/codex"), check=True)

    def test_install_command_current_uses_windows_override(self) -> None:
        install_command = agent._LocalAgentInstallCommand(
            ("sh", "-c", "install-agent"),
            "install-agent",
            windows_override=agent._LocalAgentInstallCommand(
                ("powershell", "-Command", "Install-Agent"),
                "Install-Agent",
            ),
        )

        with patch("dart.agent.os.name", "nt"):
            self.assertEqual(install_command.current.command, ("powershell", "-Command", "Install-Agent"))
            self.assertEqual(install_command.current.display, "Install-Agent")

    async def test_read_stream_handles_oversized_jsonl_line(self) -> None:
        reader = asyncio.StreamReader()
        payload = agent.json.dumps({"item": {"text": "x" * 70000}}) + "\n"
        emitted_lines = []

        async def on_line(line: str) -> None:
            emitted_lines.append(line)

        reader.feed_data(payload.encode())
        reader.feed_eof()

        output = await agent._read_stream(reader, on_line)

        self.assertEqual(output, payload)
        self.assertEqual(emitted_lines, [payload])

    async def test_run_kills_process_when_stream_emit_fails(self) -> None:
        class FakeProcess:
            def __init__(self) -> None:
                self.stdout = asyncio.StreamReader()
                self.stderr = asyncio.StreamReader()
                self.returncode: int | None = None
                self.killed = False
                self.wait_future = asyncio.get_running_loop().create_future()

                self.stdout.feed_data(b'{"item":{"text":"hello"}}\n')
                self.stderr.feed_eof()

            async def wait(self) -> int:
                return await self.wait_future

            def kill(self) -> None:
                self.killed = True
                self.returncode = -9
                self.stdout.feed_eof()
                if not self.wait_future.done():
                    self.wait_future.set_result(self.returncode)

        fake_process = FakeProcess()

        async def fake_create_subprocess_exec(*args, **kwargs):
            return fake_process

        async def emit_event(event):
            raise RuntimeError("send failed")

        with patch("dart.agent.asyncio.create_subprocess_exec", new=fake_create_subprocess_exec):
            with self.assertRaisesRegex(RuntimeError, "send failed"):
                await agent._LOCAL_AGENTS["codex"].run("Say hello", None, None, None, (), emit_event)

        self.assertTrue(fake_process.killed)

    async def test_run_returns_parsed_failure_message_for_nonzero_exit(self) -> None:
        gemini_message = (
            "Please set an Auth method in your /tmp/gemini/settings.json or specify one of the following "
            "environment variables before running: GEMINI_API_KEY, GOOGLE_GENAI_USE_VERTEXAI, "
            "GOOGLE_GENAI_USE_GCA"
        )

        class FakeProcess:
            def __init__(self) -> None:
                self.stdout = asyncio.StreamReader()
                self.stderr = asyncio.StreamReader()
                self.returncode = 41

                self.stdout.feed_data(
                    agent.json.dumps(
                        {
                            "session_id": "session-1",
                            "error": {"type": "Error", "message": gemini_message, "code": 41},
                        }
                    ).encode()
                )
                self.stdout.feed_eof()
                self.stderr.feed_data(b"YOLO mode is enabled. All tool calls will be automatically approved.\n")
                self.stderr.feed_eof()

            async def wait(self) -> int:
                return self.returncode

            def kill(self) -> None:
                pass

        fake_process = FakeProcess()
        emitted_events = []

        async def fake_create_subprocess_exec(*args, **kwargs):
            return fake_process

        async def emit_event(event):
            emitted_events.append(event)

        with patch("dart.agent.asyncio.create_subprocess_exec", new=fake_create_subprocess_exec):
            success, message, session_id = await agent._LOCAL_AGENTS["gemini"].run(
                "Say hello", None, None, None, (), emit_event
            )

        self.assertFalse(success)
        self.assertIsInstance(message, str)
        self.assertEqual(message, gemini_message)
        self.assertIsNone(session_id)
        self.assertEqual(emitted_events, [])

    async def test_run_until_closed_ignores_unsupported_stdin_reader(self) -> None:
        class Stdin:
            def fileno(self) -> int:
                return 0

            def isatty(self) -> bool:
                return True

        class Websocket:
            def __init__(self) -> None:
                self.closed = False

            async def close(self) -> None:
                self.closed = True

        async def handle_messages(websocket, quiet, agent_id, base_url, headers, ui, install):
            return True

        websocket = Websocket()
        loop = asyncio.get_running_loop()
        with (
            patch("dart.agent.sys.stdin", new=Stdin()),
            patch.object(loop, "add_reader", side_effect=NotImplementedError),
            patch("dart.agent._handle_messages", new=handle_messages),
        ):
            result = await agent._run_until_closed_or_eof(
                websocket,
                False,
                "never",
                agent_id="agent-1",
                base_url="https://dart.test",
                headers={},
                ui=agent.AgentUI(),
            )

        self.assertTrue(result)
        self.assertFalse(websocket.closed)


if __name__ == "__main__":
    unittest.main()
