#!/usr/bin/env python3
"""Exercise the selected shell tool through reads, edits, failure and recovery."""

import json
import threading
from http.server import ThreadingHTTPServer

from protocol_fixture_server import FixtureHandler, chunk


STEPS = [
    ("cat INPUT.txt", "status=old"),
    ("grep '^status=' INPUT.txt", "status=old"),
    ("sed 's/status=old/status=new/' INPUT.txt > OUTPUT.txt", "(no output)"),
    ("sh -c 'exit 7'", "Command exited with code 7"),
    ("test \"$(cat OUTPUT.txt)\" = status=new && printf 'recovery verified\\n'", "recovery verified"),
]


class ShellHandler(FixtureHandler):
    request_count = 0
    failure = None

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self.send_error(404)
            return
        type(self).request_count += 1
        turn = type(self).request_count - 1
        try:
            request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert request.get("stream") is True, "streaming required"
            names = [tool["function"]["name"] for tool in request["tools"]]
            assert names == ["bash"], "fixture must use the selected shell-only profile"
            messages = request["messages"]
            calls = [call for message in messages for call in message.get("tool_calls", [])]
            results = [message for message in messages if message["role"] == "tool"]
            assert len(calls) == len(results) == turn, "history count or ordering lost"
            for index, (call, result) in enumerate(zip(calls, results)):
                call_id = f"call_shell_fixture_{index}"
                assert call["id"] == result["tool_call_id"] == call_id, "call identity changed"
                assert call["function"]["name"] == "bash", "tool changed"
                assert json.loads(call["function"]["arguments"]) == {"command": STEPS[index][0]}, "arguments changed"
                assert STEPS[index][1] in str(result["content"]), "tool result lost or failed"
            assert turn <= len(STEPS), "unexpected extra turn"
            if turn == len(STEPS):
                frames = [chunk({"role": "assistant", "content": "Shell protocol fixture passed."}), chunk({}, "stop")]
            else:
                arguments = json.dumps({"command": STEPS[turn][0]})
                midpoint = len(arguments) // 2
                frames = [
                    chunk({"role": "assistant", "tool_calls": [{"index": 0,
                        "id": f"call_shell_fixture_{turn}", "type": "function",
                        "function": {"name": "bash", "arguments": arguments[:midpoint]}}]}),
                    chunk({"tool_calls": [{"index": 0, "function": {"arguments": arguments[midpoint:]}}]}),
                    chunk({}, "tool_calls"),
                ]
        except (AssertionError, KeyError, ValueError, IndexError) as error:
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
        if turn == len(STEPS):
            threading.Thread(target=self.server.shutdown, daemon=True).start()


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8080), ShellHandler)
    server.serve_forever()
    server.server_close()
    passed = not ShellHandler.failure and ShellHandler.request_count == len(STEPS) + 1
    print("shell protocol fixture:", "PASS" if passed else f"FAIL: {ShellHandler.failure}")
    raise SystemExit(0 if passed else 1)
