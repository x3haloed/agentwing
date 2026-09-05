#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
NODE_BIN="${AGENTWING_NODE_BIN:-/Users/chad/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node}"
if lsof -nP -iTCP:8080 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "port 8080 is occupied; do not run this fixture during inference" >&2
  exit 1
fi
TMP=$(mktemp -d)
SERVER_PID=""
PI_PID=""
cleanup() {
  if [ -n "$PI_PID" ]; then
    kill -KILL "-$PI_PID" 2>/dev/null || true
    wait "$PI_PID" 2>/dev/null || true
  fi
  if [ -n "$SERVER_PID" ]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  if [ -n "${AGENTWING_VALIDATION_DIR:-}" ]; then
    cp "$TMP/pi.jsonl" "$TMP/pi.stderr" "$TMP/server.log" "$AGENTWING_VALIDATION_DIR/" 2>/dev/null || true
  fi
  # This directory and all its contents were created by this disposable fixture.
  rm -rf "$TMP"
}
trap cleanup EXIT INT TERM
if [ -n "${AGENTWING_VALIDATION_DIR:-}" ]; then
  mkdir -p "$(dirname "$AGENTWING_VALIDATION_DIR")"
  mkdir "$AGENTWING_VALIDATION_DIR"  # Fresh evidence only; never overwrite a previous probe.
fi
mkdir "$TMP/workspace"
printf 'status=old\n' >"$TMP/workspace/INPUT.txt"
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 "$ROOT/tests/shell_protocol_fixture_server.py" >"$TMP/server.log" 2>&1 &
SERVER_PID=$!
i=0
while ! curl --silent --fail http://127.0.0.1:8080/v1/models >/dev/null 2>&1; do
  kill -0 "$SERVER_PID" 2>/dev/null || { cat "$TMP/server.log"; exit 1; }
  i=$((i + 1))
  [ "$i" -lt 30 ] || { echo "fixture startup timed out" >&2; exit 1; }
  sleep 0.1
done
set +e
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 "$ROOT/scripts/exec_process_group.py" -- \
  /usr/bin/python3 "$ROOT/scripts/run_task_boundary.py" \
  --workspace "$TMP/workspace" --models-file "$ROOT/config/pi-models-stage-a.json" \
  --port 8080 -- "$NODE_BIN" "$ROOT/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js" \
  --provider agentwing-swiftlet --model qwen3.6-35b-a3b-8bit-qpack \
  --mode json --print --no-session --approve --offline --tools bash \
  --system-prompt "Complete the requested shell task and verify the result." \
  "Read INPUT.txt, update its status in OUTPUT.txt, recover from a failed command, and verify." \
  >"$TMP/pi.jsonl" 2>"$TMP/pi.stderr" &
PI_PID=$!
i=0
while kill -0 "$PI_PID" 2>/dev/null; do
  if [ "$i" -ge 300 ]; then
    echo "Pi boundary fixture exceeded 30 seconds" >>"$TMP/pi.stderr"
    kill -KILL "-$PI_PID" 2>/dev/null || true
    break
  fi
  i=$((i + 1))
  sleep 0.1
done
wait "$PI_PID"
pi_status=$?
PI_PID=""
set -e
if [ "$pi_status" -ne 0 ]; then
  cat "$TMP/pi.stderr" >&2
  exit "$pi_status"
fi
i=0
while kill -0 "$SERVER_PID" 2>/dev/null; do
  i=$((i + 1))
  [ "$i" -lt 50 ] || { echo "protocol fixture did not complete" >&2; exit 1; }
  sleep 0.1
done
wait "$SERVER_PID"
SERVER_PID=""
grep -F 'shell protocol fixture: PASS' "$TMP/server.log" >/dev/null
test "$(cat "$TMP/workspace/OUTPUT.txt")" = status=new
jq -es '[.[] | select(.type == "tool_execution_end")] | length == 5 and (map(select(.isError == true)) | length == 1)' "$TMP/pi.jsonl" >/dev/null
echo "Pi shell protocol under task write/network boundary: PASS"
