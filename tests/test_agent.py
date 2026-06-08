import asyncio
import unittest
from unittest.mock import call, patch

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

        async def fake_run_local_agent(local_agent_name, prompt, message_id, emit_event):
            await emit_event({"kind": "text_delta", "text": "hello"})
            await emit_event({"kind": "thinking", "detail": "done thinking"})
            return True, "hello"

        work = {"type": "message", "id": "work-1", "localAgent": "codex", "prompt": "Say hello"}
        with patch("dart.agent._run_local_agent", new=fake_run_local_agent):
            await agent._handle_work(Websocket(), work, quiet=True)

        parsed_payloads = [agent.json.loads(payload) for payload in sent_payloads]
        self.assertEqual([payload["sequence"] for payload in parsed_payloads], [1, 2, 3])
        self.assertEqual(parsed_payloads[0]["event"], {"kind": "text_delta", "text": "hello"})
        self.assertEqual(parsed_payloads[1]["event"], {"kind": "thinking", "detail": "done thinking"})
        self.assertEqual(parsed_payloads[2]["event"], {"kind": "done", "success": True, "message": "hello"})

    async def test_handle_work_prints_streamed_text_as_it_arrives(self) -> None:
        class Websocket:
            async def send(self, payload: str) -> None:
                pass

        async def fake_run_local_agent(local_agent_name, prompt, message_id, emit_event):
            await emit_event({"kind": "text_delta", "text": "hello"})
            await emit_event({"kind": "tool_call", "toolCallId": "toolu-1", "name": "Read", "args": {}})
            await emit_event({"kind": "text_delta", "text": "again"})
            return True, "hello"

        work = {"type": "message", "id": "work-1", "localAgent": "codex", "prompt": "Say hello"}
        with patch("dart.agent._run_local_agent", new=fake_run_local_agent), patch("builtins.print") as print_mock:
            await agent._handle_work(Websocket(), work, quiet=False)

        self.assertEqual(print_mock.mock_calls.count(call("\nAssistant: ", end="", flush=True)), 2)
        self.assertIn(call("hello", end="", flush=True), print_mock.mock_calls)
        self.assertIn(call("again", end="", flush=True), print_mock.mock_calls)
        self.assertNotIn(call("\nAssistant: hello", flush=True), print_mock.mock_calls)

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
                await agent._LOCAL_AGENTS["codex"].run("Say hello", None, emit_event)

        self.assertTrue(fake_process.killed)


if __name__ == "__main__":
    unittest.main()
