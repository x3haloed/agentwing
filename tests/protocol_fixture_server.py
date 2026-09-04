#!/usr/bin/env python3
"""Two-turn OpenAI Chat Completions fixture for Pi protocol validation."""

from __future__ import annotations

import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


TOOL_CALL_ID = "call_agentwing_fixture"


def chunk(delta: dict, finish_reason: str | None = None) -> bytes:
    payload = {
        "id": "chatcmpl-agentwing-fixture",
        "object": "chat.completion.chunk",
        "created": 0,
        "model": "agentwing-protocol-fixture",
        "choices": [
            {"index": 0, "delta": delta, "finish_reason": finish_reason}
        ],
    }
    return f"data: {json.dumps(payload, separators=(',', ':'))}\n\n".encode()


class FixtureHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    request_count = 0
    failure: str | None = None

    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        if self.path != "/v1/models":
            self.send_error(404)
            return
        body = b'{"object":"list","data":[]}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/v1/chat/completions":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        request = json.loads(self.rfile.read(length))
        type(self).request_count += 1

        try:
            if type(self).request_count == 1:
                self.validate_first_turn(request)
                frames = [
                    chunk(
                        {
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "index": 0,
                                    "id": TOOL_CALL_ID,
                                    "type": "function",
                                    "function": {
                                        "name": "read",
                                        "arguments": '{"path":"TARGET.md"}',
                                    },
                                }
                            ],
                        }
                    ),
                    chunk({}, "tool_calls"),
                ]
            elif type(self).request_count == 2:
                self.validate_second_turn(request)
                frames = [
                    chunk({"role": "assistant", "content": "Protocol fixture passed."}),
                    chunk({}, "stop"),
                ]
            else:
                raise AssertionError("unexpected third completion request")
        except AssertionError as error:
            type(self).failure = str(error)
            self.send_error(400, str(error))
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return

        body = b"".join(frames) + b"data: [DONE]\n\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

        if type(self).request_count == 2:
            threading.Thread(target=self.server.shutdown, daemon=True).start()

    @staticmethod
    def validate_first_turn(request: dict) -> None:
        assert request.get("stream") is True, "Pi did not request streaming"
        names = {
            tool.get("function", {}).get("name") for tool in request.get("tools", [])
        }
        assert "read" in names, "Pi did not declare its read tool"
        assert request.get("messages", [])[-1].get("role") == "user", (
            "first request did not end in a user message"
        )

    @staticmethod
    def validate_second_turn(request: dict) -> None:
        messages = request.get("messages", [])
        assistant = next(
            (message for message in messages if message.get("tool_calls")), None
        )
        assert assistant is not None, "assistant tool call was not preserved"
        calls = assistant["tool_calls"]
        assert calls[0].get("id") == TOOL_CALL_ID, "tool-call ID changed"
        tool_result = next(
            (message for message in messages if message.get("role") == "tool"), None
        )
        assert tool_result is not None, "tool result was not returned"
        assert tool_result.get("tool_call_id") == TOOL_CALL_ID, (
            "tool result was associated with the wrong call"
        )
        assert "Agentwing" in str(tool_result.get("content")), (
            "read result did not contain the fixture file"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), FixtureHandler)
    server.serve_forever()
    if FixtureHandler.failure:
        print(f"protocol fixture: FAIL: {FixtureHandler.failure}")
        return 1
    if FixtureHandler.request_count != 2:
        print(f"protocol fixture: FAIL: expected 2 requests, got {FixtureHandler.request_count}")
        return 1
    print("protocol fixture: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
