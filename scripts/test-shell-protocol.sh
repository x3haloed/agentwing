#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if lsof -nP -iTCP:8080 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "port 8080 is occupied; do not run protocol fixtures during inference" >&2
  exit 1
fi
TMP=$(mktemp -d)
SERVER_PID=""
cleanup() {
  if [ -n "$SERVER_PID" ]; then kill "$SERVER_PID" 2>/dev/null || true; fi
  rm -f "$TMP/INPUT.txt" "$TMP/OUTPUT.txt" "$TMP/server.log" "$TMP/pi.jsonl"
  rmdir "$TMP" 2>/dev/null || true
}
trap cleanup EXIT INT TERM
printf 'status=old\n' >"$TMP/INPUT.txt"
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 "$ROOT/tests/shell_protocol_fixture_server.py" >"$TMP/server.log" 2>&1 &
SERVER_PID=$!
i=0
while ! curl --silent --fail http://127.0.0.1:8080/v1/models >/dev/null 2>&1; do
  kill -0 "$SERVER_PID" 2>/dev/null || { cat "$TMP/server.log"; exit 1; }
  i=$((i + 1))
  [ "$i" -lt 30 ] || { echo "fixture startup timed out" >&2; exit 1; }
  sleep 0.1
done
(cd "$TMP" && "$ROOT/scripts/pi.sh" --mode json --print --no-session --approve --offline \
  --tools bash --system-prompt "Complete the requested shell task and verify the result." \
  "Read INPUT.txt, update its status in OUTPUT.txt, recover from a failed command, and verify.") >"$TMP/pi.jsonl" 2>&1
wait "$SERVER_PID"
SERVER_PID=""
grep -F 'shell protocol fixture: PASS' "$TMP/server.log" >/dev/null
test "$(cat "$TMP/OUTPUT.txt")" = status=new
jq -es '[.[] | select(.type == "tool_execution_end")] | length == 5 and (map(select(.isError == true)) | length == 1)' "$TMP/pi.jsonl" >/dev/null
echo "Pi shell read/search/edit/failure/recovery protocol fixture: PASS"
