#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DEPS="$ROOT/spec/dependencies.json"
SWIFTLET=$(jq -r '.swiftlet.local_path' "$DEPS")
MODEL=$(jq -r '.qwen3_6_35b_a3b_8bit_qpack.local_path' "$DEPS")
RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)
EVIDENCE_ROOT="${AGENTWING_EVIDENCE_ROOT:-/Users/chad/Models/agentwing/evidence/AW-0002}"
RUN_DIR="$EVIDENCE_ROOT/$RUN_ID"
FIXTURE=$(mktemp -d)
SERVER_PID=""
PI_PID=""

swap_used_mib() {
  sysctl -n vm.swapusage | awk '{
    for (i = 1; i <= NF; i++) if ($i == "used") {
      value = $(i + 2); sub(/M$/, "", value); print value; exit
    }
  }'
}

cleanup() {
  if [ -n "$PI_PID" ]; then kill "$PI_PID" 2>/dev/null || true; fi
  if [ -n "$SERVER_PID" ]; then kill "$SERVER_PID" 2>/dev/null || true; fi
  rm -f "$FIXTURE/TARGET.md"
  rmdir "$FIXTURE" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

if lsof -nP -iTCP:8080 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "port 8080 already has a listener" >&2
  exit 1
fi
if pgrep -f 'swiftlet-server|swiftlet generate|TurboFieldfare|mlx_lm.server|llama-server|ollama runner' >/dev/null 2>&1; then
  echo "another model-owning process is already running" >&2
  pgrep -fl 'swiftlet-server|swiftlet generate|TurboFieldfare|mlx_lm.server|llama-server|ollama runner' >&2 || true
  exit 1
fi

mkdir -p "$RUN_DIR"
cp "$ROOT/TARGET.md" "$FIXTURE/TARGET.md"
baseline_swap=$(swap_used_mib)
printf 'timestamp_utc\tpressure_level\tswap_used_mib\n' >"$RUN_DIR/pressure.tsv"

"$SWIFTLET/.build/release/swiftlet-server" \
  --model "$MODEL" --port 8080 --cache-gb 0.5 \
  >"$RUN_DIR/server.log" 2>&1 &
SERVER_PID=$!

i=0
while ! curl --silent --fail http://127.0.0.1:8080/v1/models >/dev/null 2>&1; do
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "Swiftlet exited during startup" >&2
    exit 1
  fi
  i=$((i + 1))
  if [ "$i" -ge 120 ]; then
    echo "Swiftlet did not become ready within 60 seconds" >&2
    exit 1
  fi
  sleep 0.5
done

(
  cd "$FIXTURE"
  AGENTWING_PI_MODELS_FILE="$ROOT/config/pi-models-smoke.json" \
    "$ROOT/scripts/pi.sh" --print --no-session --approve --tools read \
    --system-prompt "Use the read tool exactly once when asked. Then answer briefly." \
    "Read TARGET.md and report its first Markdown heading."
) >"$RUN_DIR/pi.log" 2>&1 &
PI_PID=$!

status="running"
samples=0
while kill -0 "$PI_PID" 2>/dev/null; do
  pressure=$(sysctl -n kern.memorystatus_vm_pressure_level 2>/dev/null || echo 0)
  swap=$(swap_used_mib)
  printf '%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$pressure" "$swap" \
    >>"$RUN_DIR/pressure.tsv"
  delta=$(awk -v now="$swap" -v before="$baseline_swap" 'BEGIN { print now - before }')
  if [ "$pressure" -ge 4 ]; then
    status="stopped-critical-pressure"
    kill "$PI_PID" 2>/dev/null || true
    break
  fi
  if awk -v delta="$delta" 'BEGIN { exit !(delta > 1024) }'; then
    status="stopped-swap-growth"
    kill "$PI_PID" 2>/dev/null || true
    break
  fi
  samples=$((samples + 1))
  if [ "$samples" -ge 180 ]; then
    status="stopped-timeout"
    kill "$PI_PID" 2>/dev/null || true
    break
  fi
  sleep 5
done

set +e
wait "$PI_PID"
pi_status=$?
set -e
PI_PID=""
if [ "$status" = "running" ]; then
  if [ "$pi_status" -eq 0 ]; then status="completed"; else status="pi-failed"; fi
fi

kill "$SERVER_PID" 2>/dev/null || true
set +e
wait "$SERVER_PID"
server_status=$?
set -e
SERVER_PID=""

final_swap=$(swap_used_mib)
final_delta=$(awk -v now="$final_swap" -v before="$baseline_swap" 'BEGIN { print now - before }')
printf '%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  "$(sysctl -n kern.memorystatus_vm_pressure_level 2>/dev/null || echo 0)" "$final_swap" \
  >>"$RUN_DIR/pressure.tsv"

echo "run_dir=$RUN_DIR"
echo "status=$status"
echo "pi_exit=$pi_status"
echo "server_exit=$server_status"
echo "swap_before_mib=$baseline_swap"
echo "swap_after_mib=$final_swap"
echo "swap_delta_mib=$final_delta"
shasum -a 256 "$RUN_DIR/server.log" "$RUN_DIR/pi.log" "$RUN_DIR/pressure.tsv"
test "$status" = "completed"
