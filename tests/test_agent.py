import asyncio
import io
import unittest
from unittest.mock import AsyncMock, Mock, patch

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

    async def _run_jsonl_agent(self, name, values, *, returncode=0):
        stdout = "\n".join(agent.json.dumps(value) for value in values).encode()
        process = Mock(
            stdout=Mock(read=AsyncMock(side_effect=[stdout, b""])),
            stderr=Mock(read=AsyncMock(return_value=b"")),
            wait=AsyncMock(return_value=returncode),
            returncode=returncode,
        )
        emit_event = AsyncMock()
        with patch("dart.agent.asyncio.create_subprocess_exec", new=AsyncMock(return_value=process)):
            result = await agent._LOCAL_AGENTS[name].run("prompt", None, None, None, (), emit_event)
        return result, [call.args[0] for call in emit_event.await_args_list]

    def test_configured_agents_extract_text_delta_from_response_keys(self) -> None:
        cases = {
            "codex": (
                {"type": "item.completed", "item": {"type": "agent_message", "text": "codex text"}},
                "codex text",
            ),
            "copilot": (
                {"type": "assistant.message", "data": {"content": "copilot text", "phase": "final_answer"}},
                "copilot text",
            ),
            "gemini": ({"response": "gemini text"}, "gemini text"),
            "opencode": (
                {"type": "text", "part": {"type": "text", "text": "opencode text"}},
                "opencode text",
            ),
            "agy": ({"event": "step_update", "step_update": {"text_delta": "agy text"}}, "agy text"),
            "grok": ({"type": "text", "data": "grok text"}, "grok text"),
            "muse": ({"payload": {"kind": "run_output_delta", "text": "muse text"}}, "muse text"),
            "prime-agent": (
                {
                    "type": "message_end",
                    "message": {"role": "assistant", "content": [{"type": "text", "text": "prime text"}]},
                },
                "prime text",
            ),
            "vibe": (
                {"type": "message", "role": "assistant", "content": [{"type": "text", "text": "vibe text"}]},
                "vibe text",
            ),
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
            "devin": ("--permission-mode", "dangerous", "--respect-workspace-trust", "false"),
            "gemini": ("--approval-mode", "yolo", "--skip-trust"),
            "opencode": ("--dangerously-skip-permissions",),
            "agy": ("--dangerously-skip-permissions",),
            "grok": ("--always-approve",),
            "muse": ("--yolo",),
            "vibe": ("--trust",),
        }

        for name, expected_flags in cases.items():
            with self.subTest(name=name):
                local_agent = agent._LOCAL_AGENTS[name]
                command = local_agent.make_command(None, "prompt")
                self.assertTrue(all(flag in command for flag in expected_flags))
                if local_agent.resume_command is not None:
                    resume_command = local_agent.make_command("session-1", "prompt")
                    self.assertTrue(all(flag in resume_command for flag in expected_flags))

    def test_devin_uses_plain_stdout_as_response_text(self) -> None:
        message = "Added the login page in src/routes/login.tsx."

        self.assertEqual(agent._LOCAL_AGENTS["devin"].parse_output(message, ""), (message, None))

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

    async def test_codex_keeps_reasoning_out_of_answer_text(self) -> None:
        values = [
            {"type": "thread.started", "thread_id": "thread-1"},
            {"type": "item.completed", "item": {"id": "i1", "type": "reasoning", "text": "Check the tests."}},
            {"type": "item.completed", "item": {"id": "i2", "type": "reasoning", "text": "Check the tests."}},
            {"type": "item.completed", "item": {"id": "i3", "type": "agent_message", "text": "All tests pass."}},
        ]

        result, events = await self._run_jsonl_agent("codex", values)

        self.assertEqual(result, (True, "All tests pass.", "thread-1"))
        self.assertEqual(
            events,
            [
                {"kind": "thinking", "detail": "Check the tests."},
                {"kind": "thinking", "detail": "Check the tests."},
                {"kind": "text_delta", "text": "All tests pass."},
            ],
        )

    async def test_codex_still_accepts_legacy_message_events(self) -> None:
        values = [
            {"id": "submission-1", "msg": {"type": "agent_reasoning", "text": "Check the tests."}},
            {"id": "submission-1", "msg": {"type": "agent_message", "message": "All tests pass."}},
        ]

        result, events = await self._run_jsonl_agent("codex", values)

        self.assertEqual(result, (True, "All tests pass.", None))
        self.assertEqual(
            events,
            [
                {"kind": "thinking", "detail": "Check the tests."},
                {"kind": "text_delta", "text": "All tests pass."},
            ],
        )

    async def test_opencode_emits_completed_reasoning_separately_from_text(self) -> None:
        local_agent = agent._LOCAL_AGENTS["opencode"]
        for session_id in (None, "session-1"):
            self.assertIn("--thinking", local_agent.make_command(session_id, "prompt"))
        values = [
            {
                "type": "reasoning",
                "sessionID": "session-1",
                "part": {
                    "id": part_id,
                    "type": "reasoning",
                    "text": "Check the tests.",
                    "time": {"start": 1, "end": 2},
                },
            }
            for part_id in ("p1", "p2")
        ]
        values.append({"type": "text", "part": {"id": "p3", "type": "text", "text": "All tests pass."}})

        result, events = await self._run_jsonl_agent("opencode", values)

        self.assertEqual(result, (True, "All tests pass.", "session-1"))
        self.assertEqual(
            events,
            [
                {"kind": "thinking", "detail": "Check the tests."},
                {"kind": "thinking", "detail": "Check the tests."},
                {"kind": "text_delta", "text": "All tests pass."},
            ],
        )

    async def test_reasoning_only_jsonl_does_not_fall_back_to_raw_json_answer(self) -> None:
        cases = {
            "codex": {"type": "item.completed", "item": {"type": "reasoning", "text": "Check the tests."}},
            "opencode": {"type": "reasoning", "part": {"type": "reasoning", "text": "Check the tests."}},
            "grok": {"type": "thought", "data": "Check the tests."},
            "cursor": {"type": "thinking", "subtype": "delta", "text": "Check the tests."},
        }
        for name, value in cases.items():
            with self.subTest(name=name):
                result, events = await self._run_jsonl_agent(name, [value])
                self.assertEqual(result, (True, "Done.", None))
                self.assertEqual(events, [{"kind": "thinking", "detail": "Check the tests."}])

    def test_claude_preserves_identical_thoughts_with_distinct_envelope_ids(self) -> None:
        values = [
            {
                "type": "stream_event",
                "event": {
                    "type": "content_block_delta",
                    "index": 0,
                    "delta": {"type": "thinking_delta", "thinking": "Check "},
                },
            }
        ]
        values.extend(
            {
                "type": "assistant",
                "uuid": uuid,
                "message": {"id": "msg-1", "content": [{"type": "thinking", "thinking": "Check the tests."}]},
            }
            for uuid in ("block-1", "block-1", "block-2")
        )

        events, _ = self._prepare_claude_stream_events(values)

        self.assertEqual(
            events,
            [
                {"kind": "thinking", "detail": "Check the tests."},
                {"kind": "thinking", "detail": "Check the tests."},
            ],
        )

    async def test_prime_uses_completed_thoughts_and_preserves_identical_blocks(self) -> None:
        thought = {"type": "thinking", "thinking": "Check the tests."}
        values = [
            {
                "type": event_type,
                "message": {"role": "assistant", "timestamp": 1, "content": content},
                "assistantMessageEvent": update,
            }
            for event_type, content, update in (
                ("message_start", [], None),
                (
                    "message_update",
                    [{"type": "thinking", "thinking": "Check "}],
                    {
                        "type": "thinking_delta",
                        "contentIndex": 0,
                        "delta": "Check ",
                    },
                ),
                (
                    "message_update",
                    [thought],
                    {
                        "type": "thinking_end",
                        "contentIndex": 0,
                        "content": "Check the tests.",
                    },
                ),
                (
                    "message_update",
                    [thought, thought],
                    {
                        "type": "thinking_end",
                        "contentIndex": 1,
                        "content": "Check the tests.",
                    },
                ),
                (
                    "message_update",
                    [thought, thought, {"type": "text", "text": "Let me"}],
                    {
                        "type": "text_delta",
                        "contentIndex": 2,
                        "delta": "Let me",
                    },
                ),
                (
                    "message_update",
                    [thought, thought, {"type": "text", "text": "Let me check."}],
                    {
                        "type": "text_delta",
                        "contentIndex": 2,
                        "delta": " check.",
                    },
                ),
                ("message_end", [thought, thought, {"type": "text", "text": "Let me check."}], None),
                ("turn_end", [thought, thought, {"type": "text", "text": "Let me check."}], None),
                ("message_start", [], None),
                (
                    "message_update",
                    [thought],
                    {
                        "type": "thinking_end",
                        "contentIndex": 0,
                        "content": "Check the tests.",
                    },
                ),
                ("message_end", [thought], None),
                ("turn_end", [thought], None),
            )
        ]

        _, events = await self._run_jsonl_agent("prime-agent", values)

        self.assertEqual(
            events,
            [
                {"kind": "thinking", "detail": "Check the tests."},
                {"kind": "thinking", "detail": "Check the tests."},
                {"kind": "text_delta", "text": "Let me"},
                {"kind": "text_delta", "text": " check."},
                {"kind": "thinking", "detail": "Check the tests."},
            ],
        )

    async def test_prime_flushes_thought_before_later_block_if_thinking_end_is_missing(self) -> None:
        cases = [
            ("text_delta", {"type": "text", "text": "Done."}, {"kind": "text_delta", "text": "Done."}),
            (
                "toolcall_end",
                {"type": "toolCall", "id": "t1", "name": "Read", "arguments": {}},
                {
                    "kind": "tool_call",
                    "toolCallId": "t1",
                    "name": "Read",
                    "args": {},
                },
            ),
        ]
        for update_type, block, expected_event in cases:
            with self.subTest(update_type=update_type):
                thought = {"type": "thinking", "thinking": "Check the tests."}
                values = [
                    {"type": "message_start", "message": {"role": "assistant", "content": []}},
                    {
                        "type": "message_update",
                        "message": {"role": "assistant", "content": [thought]},
                        "assistantMessageEvent": {
                            "type": "thinking_delta",
                            "contentIndex": 0,
                            "delta": "Check the tests.",
                        },
                    },
                    {
                        "type": "message_update",
                        "message": {"role": "assistant", "content": [thought, block]},
                        "assistantMessageEvent": {"type": update_type, "contentIndex": 1},
                    },
                    {"type": "message_end", "message": {"role": "assistant", "content": [thought, block]}},
                ]
                if update_type == "toolcall_end":
                    values.append({"type": "tool_execution_start", "toolCallId": "t1", "toolName": "Read", "args": {}})

                _, events = await self._run_jsonl_agent("prime-agent", values)

                self.assertEqual(events, [{"kind": "thinking", "detail": "Check the tests."}, expected_event])

    async def test_prime_preserves_order_when_message_start_contains_final_snapshot(self) -> None:
        message = {
            "role": "assistant",
            "content": [
                {"type": "thinking", "thinking": "Check the tests."},
                {"type": "text", "text": "Done."},
            ],
        }
        values = [
            {"type": event_type, "message": message} for event_type in ("message_start", "message_end", "turn_end")
        ]

        _, events = await self._run_jsonl_agent("prime-agent", values)

        self.assertEqual(
            events,
            [
                {"kind": "thinking", "detail": "Check the tests."},
                {"kind": "text_delta", "text": "Done."},
            ],
        )

    async def test_prime_keeps_partial_thought_from_aborted_message_end(self) -> None:
        value = {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "stopReason": "aborted",
                "content": [{"type": "thinking", "thinking": "Check the"}],
            },
        }

        _, events = await self._run_jsonl_agent("prime-agent", [value], returncode=1)

        self.assertEqual(events, [{"kind": "thinking", "detail": "Check the"}])

    async def test_grok_buffers_thought_chunks_until_output_or_response_boundary(self) -> None:
        boundaries = [
            {"type": "text", "data": "Checking."},
            {"type": "usage", "messageId": "msg-1"},
            {"type": "end", "sessionId": "session-1"},
            {"type": "error", "message": "Interrupted."},
            {"type": "tool_call", "toolCallId": "t1", "toolName": "read_file", "status": "in_progress"},
            {"type": "tool_call_update", "toolCallId": "t1", "status": "completed", "rawOutput": "done"},
        ]
        for boundary in boundaries:
            with self.subTest(boundary=boundary["type"]):
                values = [
                    {"type": "thought", "data": "Check"},
                    {"type": "thought", "data": " "},
                    {"type": "plan", "entries": []},
                    {"type": "thought", "data": "the tests."},
                    boundary,
                    {"type": "thought", "data": ""},
                    {"type": "thought", "data": "Check the tests."},
                ]

                _, events = await self._run_jsonl_agent("grok", values)

                self.assertEqual(events[0], {"kind": "thinking", "detail": "Check the tests."})
                self.assertEqual(events[-1], {"kind": "thinking", "detail": "Check the tests."})
                self.assertEqual(sum(event["kind"] == "thinking" for event in events), 2)

    async def test_grok_flushes_unfinished_thought_on_success_or_failure(self) -> None:
        for returncode in (0, 1):
            with self.subTest(returncode=returncode):
                result, events = await self._run_jsonl_agent(
                    "grok",
                    [
                        {"type": "thought", "data": "Still "},
                        {"type": "thought", "data": "thinking."},
                    ],
                    returncode=returncode,
                )
                self.assertEqual(result[0], returncode == 0)
                self.assertEqual(events, [{"kind": "thinking", "detail": "Still thinking."}])

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

    async def test_cursor_buffers_thinking_deltas_and_preserves_adjacent_thoughts(self) -> None:
        emitted_events = []
        chunks = iter(
            (
                [
                    {"type": "thinking", "subtype": "delta", "text": "Think"},
                    {"type": "thinking", "subtype": "delta", "text": " "},
                    {"type": "thinking", "subtype": "delta", "text": "carefully."},
                ],
                [
                    {"type": "thinking", "subtype": "completed"},
                    {"type": "thinking", "subtype": "delta", "text": "Think carefully."},
                    {"type": "thinking", "subtype": "completed"},
                    {"type": "thinking", "subtype": "delta", "text": ""},
                    {"type": "thinking", "subtype": "completed"},
                    {
                        "type": "tool_call",
                        "subtype": "started",
                        "call_id": "call-1",
                        "name": "Read",
                        "args": {"path": "README.md"},
                    },
                    {"type": "assistant", "message": {"content": [{"type": "text", "text": "Done."}]}},
                    {"type": "result", "result": "Done.", "session_id": "session-1"},
                ],
            )
        )

        async def read_stdout(size):
            values = next(chunks, None)
            if values is None:
                return b""
            self.assertEqual(emitted_events, [])
            return "".join(agent.json.dumps(value) + "\n" for value in values).encode()

        process = Mock(
            stdout=Mock(read=AsyncMock(side_effect=read_stdout)),
            stderr=Mock(read=AsyncMock(return_value=b"")),
            wait=AsyncMock(return_value=0),
            returncode=0,
        )

        async def emit_event(event):
            emitted_events.append(event)

        with patch("dart.agent.asyncio.create_subprocess_exec", new=AsyncMock(return_value=process)):
            result = await agent._LOCAL_AGENTS["cursor"].run("Think carefully", None, None, None, (), emit_event)

        self.assertEqual(result, (True, "Done.", "session-1"))
        self.assertEqual(
            emitted_events,
            [
                {"kind": "thinking", "detail": "Think carefully."},
                {"kind": "thinking", "detail": "Think carefully."},
                {"kind": "tool_call", "toolCallId": "call-1", "name": "Read", "args": {"path": "README.md"}},
                {"kind": "text_delta", "text": "Done."},
            ],
        )

    async def test_cursor_flushes_unfinished_thinking_before_later_output_or_exit(self) -> None:
        for returncode, stream_text in ((0, False), (1, False), (0, True)):
            with self.subTest(returncode=returncode, stream_text=stream_text):
                values = [
                    {"type": "thinking", "subtype": "delta", "text": "Still "},
                    {"type": "thinking", "subtype": "delta", "text": "thinking."},
                ]
                if stream_text:
                    values.append({"type": "assistant", "message": {"content": [{"type": "text", "text": "Done."}]}})
                if returncode == 0:
                    values.append({"type": "result", "result": "Done.", "session_id": "session-1"})
                stdout = "\n".join(agent.json.dumps(value) for value in values).encode()
                process = Mock(
                    stdout=Mock(read=AsyncMock(side_effect=[stdout, b""])),
                    stderr=Mock(read=AsyncMock(side_effect=[b"Process failed.", b""])),
                    wait=AsyncMock(return_value=returncode),
                    returncode=returncode,
                )
                emit_event = AsyncMock()

                with patch("dart.agent.asyncio.create_subprocess_exec", new=AsyncMock(return_value=process)):
                    success, _, _ = await agent._LOCAL_AGENTS["cursor"].run(
                        "Think carefully", None, None, None, (), emit_event
                    )

                self.assertEqual(success, returncode == 0)
                events = [call.args[0] for call in emit_event.await_args_list]
                expected_events = [{"kind": "thinking", "detail": "Still thinking."}]
                if returncode == 0:
                    expected_events.append({"kind": "text_delta", "text": "Done."})
                self.assertEqual(events, expected_events)

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

    async def test_handle_work_fails_when_attachment_download_fails(self) -> None:
        sent_payloads = []

        class Websocket:
            async def send(self, payload: str) -> None:
                sent_payloads.append(payload)

        work = {
            "type": "message",
            "id": "work-1",
            "localAgent": "codex",
            "prompt": "Describe the screenshot",
            "attachments": [{"type": "file", "name": "screenshot.png", "url": "/api/attachments/attachment-1"}],
        }
        with (
            patch("dart.agent._run_local_agent") as run_mock,
            patch("dart.agent.urlopen", side_effect=TimeoutError("timed out")),
        ):
            await agent._handle_work(
                Websocket(), work, quiet=True, base_url="https://dart.test", headers={}, ui=agent.AgentUI()
            )

        run_mock.assert_not_called()
        self.assertEqual(
            [agent.json.loads(payload)["event"] for payload in sent_payloads],
            [{"kind": "done", "success": False, "message": "Failed to load attachments: timed out."}],
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
                self.sent: list[str] = []

            def __aiter__(self):
                return self

            async def __anext__(self) -> str:
                if not self.messages:
                    raise StopAsyncIteration
                return self.messages.pop(0)

            async def send(self, message: str) -> None:
                self.sent.append(message)

        ui = Mock()
        websocket = Websocket()
        with (
            patch("dart.agent._validate_local_agent_available"),
            patch("dart.agent.subprocess.run", return_value=Mock(returncode=0)),
            patch.dict("dart.agent.os.environ", {agent.AGENT_CONNECTION_LOG_PATH_ENVVAR: "/tmp/dart-agent.log"}),
        ):
            await agent._handle_messages(websocket, True, "agent-1", "https://dart.test", {}, ui, "never")

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
            patch("dart.agent.shutil.which", side_effect=[None, "/usr/local/bin/npm", "/usr/local/bin/codex"]),
            patch("dart.agent.subprocess.run") as run_mock,
            patch("builtins.print"),
        ):
            agent._validate_local_agent_available("codex", "auto")

        run_mock.assert_called_once_with(("/usr/local/bin/npm", "install", "-g", "@openai/codex"), check=True)

    def test_is_logged_in_uses_status_command_then_credentials_path(self) -> None:
        with patch("dart.agent.subprocess.run", return_value=Mock(returncode=0, stdout='{"loggedIn": false}')):
            self.assertFalse(agent._LOCAL_AGENTS["claude"].is_logged_in())
            self.assertTrue(agent._LOCAL_AGENTS["codex"].is_logged_in())

        with patch("dart.agent.subprocess.run", return_value=Mock(returncode=1, stdout="")):
            self.assertFalse(agent._LOCAL_AGENTS["codex"].is_logged_in())

        with patch.object(agent._LocalAgent, "_has_credentials", return_value=False):
            self.assertFalse(agent._LOCAL_AGENTS["grok"].is_logged_in())

        with patch("dart.agent.subprocess.run", side_effect=FileNotFoundError):
            self.assertIsNone(agent._LOCAL_AGENTS["copilot"].is_logged_in())

    async def test_stream_local_agent_state_reports_the_login_state_and_folder(self) -> None:
        websocket = Mock()
        websocket.send = AsyncMock()

        with (
            patch.object(agent._LocalAgent, "_has_credentials", return_value=True),
            patch("dart.agent.Path.cwd", return_value=agent.Path.home() / "projects" / "dart"),
        ):
            await agent._stream_local_agent_state(websocket, agent._LOCAL_AGENTS["grok"])

        websocket.send.assert_awaited_once_with(
            agent.json.dumps(
                {
                    "type": "state",
                    "state": {"loggedIn": True, "loginCommand": "grok login", "folder": "~/projects/dart"},
                }
            )
        )

    def test_ensure_local_agent_logged_in_opens_login_unless_already_logged_in(self) -> None:
        with (
            patch.object(agent._LocalAgent, "_has_credentials", return_value=False),
            patch.object(agent._LocalAgent, "log_in", return_value=True) as log_in_mock,
            patch("builtins.print"),
        ):
            agent.ensure_local_agent_logged_in("grok")

        log_in_mock.assert_called_once_with()

        with (
            patch.object(agent._LocalAgent, "_has_credentials", return_value=True),
            patch.object(agent._LocalAgent, "log_in") as skipped_log_in_mock,
        ):
            agent.ensure_local_agent_logged_in("grok")

        skipped_log_in_mock.assert_not_called()

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

                self.stdout.feed_data(b'{"type":"item.completed","item":{"type":"agent_message","text":"hello"}}\n')
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
                True,
                "never",
                agent_id="agent-1",
                base_url="https://dart.test",
                headers={},
                ui=agent.AgentUI(),
            )

        self.assertTrue(result)
        self.assertFalse(websocket.closed)

    async def test_read_terminal_input_sends_typed_messages(self) -> None:
        chunks = [b"hellx", b"\x7f", b"o\r", b"/b\t", b"x\r", b"/back\r"]
        sent = []

        class Websocket:
            async def send(self, payload: str) -> None:
                sent.append(agent.json.loads(payload))

        class Stdin:
            def fileno(self) -> int:
                return 0

        def add_reader(fileno, callback) -> None:
            for _ in chunks:
                callback()

        ui = agent.AgentUI()
        ui.console = Console(file=io.StringIO())
        ui.current_chat_duid = "chat-1"
        loop = asyncio.get_running_loop()
        with (
            patch("dart.agent.sys.stdin", new=Stdin()),
            patch("dart.agent_ui.subprocess.run"),
            patch("dart.agent.os.read", side_effect=chunks),
            patch.object(loop, "add_reader", new=add_reader),
        ):
            await agent._read_terminal_input(Websocket(), ui)
            await asyncio.sleep(0)
            ui.close_prompt()

        self.assertEqual(
            sent,
            [
                {"type": "chat", "text": "hello", "chatDuid": "chat-1"},
                {"type": "chat", "text": "/backgroundx", "chatDuid": "chat-1"},
            ],
        )

    def test_task_transcript_prints_title_and_finished_activity(self) -> None:
        ui = agent.AgentUI()
        ui.console = Console(file=io.StringIO(), record=True, force_terminal=False, width=120)
        printer = agent.TerminalEventPrinter(False, ui)

        printer.start_turn(
            chat_key="session-1", chat_title="Fix [/] login", is_task=True, display_prompt="Fix login", user_name="Anna"
        )
        printer.start_working("claude")
        printer.finish("Done.", success=True)
        ui.close_active_chat_transcript()

        output = ui.console.export_text()
        self.assertIn("Task · Fix [/] login", output)
        self.assertIn("· finished", output)


if __name__ == "__main__":
    unittest.main()
