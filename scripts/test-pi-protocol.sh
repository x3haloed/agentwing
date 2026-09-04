#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PYTHON_BIN="${AGENTWING_PYTHON_BIN:-/usr/bin/python3}"
TMP=$(mktemp -d)
SERVER_PID=""

cleanup() {
  if [ -n "$SERVER_PID" ]; then
    kill "$SERVER_PID" 2>/dev/null || true
  fi
  rm -f "$TMP/TARGET.md" "$TMP/server.log" "$TMP/pi.log"
  rmdir "$TMP" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

cp "$ROOT/TARGET.md" "$TMP/TARGET.md"
"$PYTHON_BIN" "$ROOT/tests/protocol_fixture_server.py" >"$TMP/server.log" 2>&1 &
SERVER_PID=$!

i=0
while ! curl --silent --fail http://127.0.0.1:8080/v1/models >/dev/null 2>&1; do
  i=$((i + 1))
  if [ "$i" -ge 30 ]; then
    echo "protocol fixture server did not start" >&2
    exit 1
  fi
  sleep 0.1
done

(cd "$TMP" && "$ROOT/scripts/pi.sh" --print --no-session --approve --tools read \
  "Read TARGET.md, then report that you finished.") >"$TMP/pi.log" 2>&1
wait "$SERVER_PID"
SERVER_PID=""

grep -F "Protocol fixture passed." "$TMP/pi.log" >/dev/null
grep -F "protocol fixture: PASS" "$TMP/server.log" >/dev/null
echo "Pi protocol fixture: PASS"
