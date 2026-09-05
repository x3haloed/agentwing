#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MANIFEST="$ROOT/benchmarks/stage-a-v1/manifest.json"
DEPS="$ROOT/spec/dependencies.json"
SWIFTLET=$(jq -r '.swiftlet.local_path' "$DEPS")
MODEL=$(jq -r '.qwen3_6_35b_a3b_8bit_qpack.local_path' "$DEPS")
RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)
EVIDENCE_ROOT="${AGENTWING_EVIDENCE_ROOT:-/Users/chad/Models/agentwing/evidence/AW-0008}"
RUN_DIR="$EVIDENCE_ROOT/$RUN_ID"
TASK_SELECTION="01-navigation"
TASK_BOUNDARY="${AGENTWING_TASK_BOUNDARY:-0}"
NODE_BIN="${AGENTWING_NODE_BIN:-/Users/chad/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node}"
SALVAGE_TOOL_PREFIX="${AGENTWING_SALVAGE_TOOL_PREFIX:-0}"
ALLOW_REPEATED_NGRAMS="${AGENTWING_ALLOW_REPEATED_NGRAMS:-0}"
STOP_AFTER_TOOL_CALL="${AGENTWING_STOP_AFTER_TOOL_CALL:-0}"
MAX_OUTPUT_TOKENS="${AGENTWING_MAX_OUTPUT_TOKENS:-192}"
TOOL_PROFILE="${AGENTWING_TOOL_PROFILE:-full}"
PROMPT_PROFILE="${AGENTWING_PROMPT_PROFILE:-base}"
TASK_TIMEOUT_OVERRIDE="${AGENTWING_TASK_TIMEOUT_SECONDS:-}"
SERVER_PID=""
PI_PID=""

usage() {
  echo "usage: $0 [--task TASK_ID | --all]" >&2
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --task)
      [ "$#" -ge 2 ] || { usage; exit 2; }
      TASK_SELECTION=$2
      shift 2
      ;;
    --all)
      TASK_SELECTION=all
      shift
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

swap_used_mib() {
  /usr/sbin/sysctl -n vm.swapusage | awk '{
    for (i = 1; i <= NF; i++) if ($i == "used") {
      value = $(i + 2); sub(/M$/, "", value); print value; exit
    }
  }'
}

cleanup() {
  if [ -n "$PI_PID" ]; then kill -TERM "-$PI_PID" 2>/dev/null || true; fi
  if [ -n "$SERVER_PID" ]; then kill "$SERVER_PID" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM

case "$TASK_BOUNDARY" in
  0)
    permission_policy=unrestricted
    task_boundary_suffix=
    boundary_policy_sha256=
    boundary_wrapper_sha256=
    ;;
  1)
    permission_policy=workspace-state-write-local-outbound-v1
    task_boundary_suffix=-task-boundary
    boundary_policy_sha256=$(shasum -a 256 "$ROOT/config/task-boundary.sb" | awk '{print $1}')
    boundary_wrapper_sha256=$(shasum -a 256 "$ROOT/scripts/run_task_boundary.py" | awk '{print $1}')
    ;;
  *) echo "AGENTWING_TASK_BOUNDARY must be 0 or 1" >&2; exit 2 ;;
esac

case "$SALVAGE_TOOL_PREFIX" in
  0|1) ;;
  *)
    echo "AGENTWING_SALVAGE_TOOL_PREFIX must be 0 or 1" >&2
    exit 2
    ;;
esac
case "$ALLOW_REPEATED_NGRAMS" in
  0) repeat_arg=; sampler_suffix=; no_repeat_ngram=3 ;;
  1) repeat_arg=--allow-repeated-ngrams; sampler_suffix=-repeat-allowed; no_repeat_ngram=0 ;;
  *) echo "AGENTWING_ALLOW_REPEATED_NGRAMS must be 0 or 1" >&2; exit 2 ;;
esac
case "$STOP_AFTER_TOOL_CALL" in
  0) boundary_arg=; boundary_suffix= ;;
  1) boundary_arg=--stop-after-tool-call; boundary_suffix=-tool-boundary ;;
  *) echo "AGENTWING_STOP_AFTER_TOOL_CALL must be 0 or 1" >&2; exit 2 ;;
esac
case "$MAX_OUTPUT_TOKENS" in
  ''|0*|*[!0-9]*) echo "AGENTWING_MAX_OUTPUT_TOKENS must be an integer from 1 to 4096" >&2; exit 2 ;;
esac
if [ "$MAX_OUTPUT_TOKENS" -gt 4096 ]; then
  echo "AGENTWING_MAX_OUTPUT_TOKENS must be at most 4096" >&2
  exit 2
fi
if [ "$MAX_OUTPUT_TOKENS" = 192 ]; then output_suffix=; else output_suffix=-max${MAX_OUTPUT_TOKENS}; fi
case "$TOOL_PROFILE" in
  full)
    tools_csv=read,bash,edit,write,grep,find,ls
    ;;
  shell)
    tools_csv=bash
    ;;
  *)
    echo "AGENTWING_TOOL_PROFILE must be full or shell" >&2
    exit 2
    ;;
esac
case "$PROMPT_PROFILE" in
  base)
    system_prompt="Complete the requested repository task autonomously. Use targeted reads and searches; do not dump whole files when a bounded read or search is enough. Keep tool arguments and final text concise. If a command fails, diagnose and recover. Do not ask questions."
    ;;
  compact-shell|environment-shell)
    if [ "$TOOL_PROFILE" != shell ]; then
      echo "AGENTWING_PROMPT_PROFILE=$PROMPT_PROFILE requires AGENTWING_TOOL_PROFILE=shell" >&2
      exit 2
    fi
    system_prompt="Work autonomously using bash. The current working directory is the task root: use relative paths only. Prefer one bounded shell command that searches only needed files, performs requested changes, and runs available project tests. Do not narrate before tool calls. After the requested artifact and validation are correct, stop immediately. If a command fails, repair it without repeating successful exploration."
    if [ "$PROMPT_PROFILE" = environment-shell ]; then
      system_prompt="$system_prompt Environment: python3 and standard-library unittest are available; python and pytest are unavailable. Discover the project's test command from its files instead of assuming a test runner."
    fi
    ;;
  *)
    echo "AGENTWING_PROMPT_PROFILE must be base, compact-shell, or environment-shell" >&2
    exit 2
    ;;
esac
if [ -n "$TASK_TIMEOUT_OVERRIDE" ]; then
  case "$TASK_TIMEOUT_OVERRIDE" in
    *[!0-9]*|0)
      echo "AGENTWING_TASK_TIMEOUT_SECONDS must be a positive integer" >&2
      exit 2
      ;;
  esac
  task_timeout_seconds=$TASK_TIMEOUT_OVERRIDE
else
  task_timeout_seconds=$(jq -r '.default_timeout_seconds' "$MANIFEST")
fi

if [ "$TASK_SELECTION" = all ]; then
  TASKS=$(jq -r '.tasks[].id' "$MANIFEST")
elif jq -e --arg id "$TASK_SELECTION" '.tasks[] | select(.id == $id)' "$MANIFEST" >/dev/null; then
  TASKS=$TASK_SELECTION
else
  echo "unknown Stage A task: $TASK_SELECTION" >&2
  exit 2
fi

if lsof -nP -iTCP:8080 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "port 8080 already has a listener" >&2
  exit 1
fi
if pgrep -f 'swiftlet-server|swiftlet generate|TurboFieldfare|mlx_lm.server|llama-server|ollama runner' >/dev/null 2>&1; then
  echo "another model-owning process is already running" >&2
  pgrep -fl 'swiftlet-server|swiftlet generate|TurboFieldfare|mlx_lm.server|llama-server|ollama runner' >&2 || true
  exit 1
fi
if [ ! -x "$SWIFTLET/.build/release/swiftlet-server" ]; then
  echo "Swiftlet release server is missing; build it before running Stage A" >&2
  exit 1
fi

mkdir -p "$RUN_DIR/tasks"
printf '%s\n' "$system_prompt" >"$RUN_DIR/system-prompt.txt"
system_prompt_sha256=$(shasum -a 256 "$RUN_DIR/system-prompt.txt" | awk '{print $1}')
jq --argjson maximum "$MAX_OUTPUT_TOKENS" \
  '.providers["agentwing-swiftlet"].models[0].maxTokens = $maximum' \
  "$ROOT/config/pi-models-stage-a.json" >"$RUN_DIR/pi-models.json"
pi_models_sha256=$(shasum -a 256 "$RUN_DIR/pi-models.json" | awk '{print $1}')
baseline_swap=$(swap_used_mib)
free_kib=$(df -k "$ROOT" | awk 'NR == 2 {print $4}')
suite_hash=$(find "$ROOT/benchmarks/stage-a-v1" -type f -print0 | sort -z | xargs -0 shasum -a 256 | shasum -a 256 | awk '{print $1}')
agentwing_revision=$(git -C "$ROOT" rev-parse HEAD)
swiftlet_revision=$(git -C "$SWIFTLET" rev-parse HEAD)
server_binary_sha256=$(shasum -a 256 "$SWIFTLET/.build/release/swiftlet-server" | awk '{print $1}')
os_version=$(sw_vers -productVersion)
os_build=$(sw_vers -buildVersion)
if [ "$SALVAGE_TOOL_PREFIX" = 1 ]; then
  recovery_suffix=-prefix-salvage
  salvage_arg=--salvage-tool-prefix
else
  recovery_suffix=
  salvage_arg=
fi
configuration="B0-stage-a-v1.1-${TOOL_PROFILE}-${PROMPT_PROFILE}${recovery_suffix}${sampler_suffix}${boundary_suffix}${output_suffix}${task_boundary_suffix}"

jq -n \
  --arg run_id "$RUN_ID" \
  --arg suite_id "$(jq -r '.suite_id' "$MANIFEST")" \
  --arg suite_sha256 "$suite_hash" \
  --arg agentwing_revision "$agentwing_revision" \
  --arg swiftlet_revision "$swiftlet_revision" \
  --arg server_binary_sha256 "$server_binary_sha256" \
  --arg model_revision "$(jq -r '.qwen3_6_35b_a3b_8bit_qpack.revision' "$DEPS")" \
  --arg harness_revision "$(jq -r '.pi.revision' "$DEPS")" \
  --arg os_version "$os_version" \
  --arg os_build "$os_build" \
  --arg task_selection "$TASK_SELECTION" \
  --arg configuration "$configuration" \
  --arg tool_profile "$TOOL_PROFILE" \
  --arg prompt_profile "$PROMPT_PROFILE" \
  --arg system_prompt_sha256 "$system_prompt_sha256" \
  --arg pi_models_sha256 "$pi_models_sha256" \
  --arg permission_policy "$permission_policy" \
  --arg boundary_policy_sha256 "$boundary_policy_sha256" \
  --arg boundary_wrapper_sha256 "$boundary_wrapper_sha256" \
  --argjson task_boundary "$TASK_BOUNDARY" \
  --arg tools_csv "$tools_csv" \
  --argjson salvage_tool_prefix "$SALVAGE_TOOL_PREFIX" \
  --argjson no_repeat_ngram "$no_repeat_ngram" \
  --argjson stop_after_tool_call "$STOP_AFTER_TOOL_CALL" \
  --argjson max_output_tokens "$MAX_OUTPUT_TOKENS" \
  --argjson task_timeout_seconds "$task_timeout_seconds" \
  --argjson free_kib "$free_kib" \
  --argjson baseline_swap_mib "$baseline_swap" \
  '{run_id:$run_id,suite_id:$suite_id,suite_sha256:$suite_sha256,
    configuration:$configuration,agentwing_revision:$agentwing_revision,
    swiftlet_revision:$swiftlet_revision,server_binary_sha256:$server_binary_sha256,
    model_revision:$model_revision,
    harness_revision:$harness_revision,model_cache_gb:0.5,max_output_tokens:$max_output_tokens,
    temperature:0,presence_penalty:0,frequency_penalty:0.5,
    no_repeat_ngram:$no_repeat_ngram,min_new_tokens:8,top_k:20,top_p:0.8,
    stop_after_tool_call:($stop_after_tool_call == 1),
    enable_thinking:false,tool_profile:$tool_profile,prompt_profile:$prompt_profile,
    system_prompt_sha256:$system_prompt_sha256,
    pi_models_sha256:$pi_models_sha256,
    task_boundary:($task_boundary == 1),permission_policy:$permission_policy,
    boundary_policy_sha256:$boundary_policy_sha256,
    boundary_wrapper_sha256:$boundary_wrapper_sha256,
    tools:($tools_csv|split(",")),
    bind:"127.0.0.1",storage:"internal-ssd",free_kib_before:$free_kib,
    swap_used_mib_before:$baseline_swap_mib,os_version:$os_version,os_build:$os_build,
    task_selection:$task_selection,task_timeout_seconds:$task_timeout_seconds,
    salvage_tool_prefix:($salvage_tool_prefix == 1)}' >"$RUN_DIR/manifest.json"
printf 'timestamp_utc\ttask_id\tpressure_level\tswap_used_mib\n' >"$RUN_DIR/pressure.tsv"
: >"$RUN_DIR/results.jsonl"
/usr/bin/pmset -g therm >"$RUN_DIR/thermal-before.txt" 2>&1 || true
suite_start_epoch=$(date +%s)

"$SWIFTLET/.build/release/swiftlet-server" \
  --model "$MODEL" --port 8080 --cache-gb 0.5 --debug-tool-output \
  --accept-schema-tags $salvage_arg $repeat_arg $boundary_arg >"$RUN_DIR/server.log" 2>&1 &
SERVER_PID=$!

i=0
while ! curl --silent --fail http://127.0.0.1:8080/v1/models >/dev/null 2>&1; do
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "Swiftlet exited during startup" >&2
    exit 1
  fi
  pressure=$(/usr/sbin/sysctl -n kern.memorystatus_vm_pressure_level 2>/dev/null || echo 0)
  swap=$(swap_used_mib)
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" server-startup "$pressure" "$swap" >>"$RUN_DIR/pressure.tsv"
  startup_delta=$(awk -v now="$swap" -v before="$baseline_swap" 'BEGIN { print now - before }')
  if [ "$pressure" -ge 4 ]; then
    echo "critical memory pressure during Swiftlet startup" >&2
    exit 1
  fi
  if awk -v delta="$startup_delta" 'BEGIN { exit !(delta > 1024) }'; then
    echo "swap growth exceeded 1 GiB during Swiftlet startup" >&2
    exit 1
  fi
  i=$((i + 1))
  if [ "$i" -ge 120 ]; then
    echo "Swiftlet did not become ready within 60 seconds" >&2
    exit 1
  fi
  sleep 0.5
done

suite_status=completed
for task_id in $TASKS; do
  task_dir="$RUN_DIR/tasks/$task_id"
  workspace="$task_dir/workspace"
  mkdir -p "$workspace"
  cp -R "$ROOT/benchmarks/stage-a-v1/tasks/$task_id/input/." "$workspace/"
  prompt=$(jq -r --arg id "$task_id" '.tasks[] | select(.id == $id) | .prompt' "$MANIFEST")
  timeout_seconds=$task_timeout_seconds
  start_epoch=$(date +%s)
  status=running
  server_line_at_stop=
  server_line_before=$(wc -l <"$RUN_DIR/server.log" | tr -d ' ')

  if [ "$TASK_BOUNDARY" = 1 ]; then
    set -- /usr/bin/python3 "$ROOT/scripts/run_task_boundary.py" \
      --workspace "$workspace" --models-file "$RUN_DIR/pi-models.json" --port 8080 -- \
      "$NODE_BIN" "$ROOT/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js" \
      --provider agentwing-swiftlet --model qwen3.6-35b-a3b-8bit-qpack
  else
    set -- /usr/bin/env "AGENTWING_PI_MODELS_FILE=$RUN_DIR/pi-models.json" "$ROOT/scripts/pi.sh"
  fi
  /usr/bin/python3 "$ROOT/scripts/exec_process_group.py" \
    --cwd "$workspace" -- "$@" --mode json --print --no-session --approve --offline \
    --tools "$tools_csv" \
    --system-prompt "$system_prompt" \
    "$prompt" >"$task_dir/pi.jsonl" 2>"$task_dir/pi.stderr" &
  PI_PID=$!

  while kill -0 "$PI_PID" 2>/dev/null; do
    pressure=$(/usr/sbin/sysctl -n kern.memorystatus_vm_pressure_level 2>/dev/null || echo 0)
    swap=$(swap_used_mib)
    printf '%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$task_id" "$pressure" "$swap" >>"$RUN_DIR/pressure.tsv"
    delta=$(awk -v now="$swap" -v before="$baseline_swap" 'BEGIN { print now - before }')
    elapsed=$(($(date +%s) - start_epoch))
    if [ "$pressure" -ge 4 ]; then
      status=stopped-critical-pressure
      server_line_at_stop=$(wc -l <"$RUN_DIR/server.log" | tr -d ' ')
      kill -TERM "-$PI_PID" 2>/dev/null || true
      break
    fi
    if awk -v delta="$delta" 'BEGIN { exit !(delta > 1024) }'; then
      status=stopped-swap-growth
      server_line_at_stop=$(wc -l <"$RUN_DIR/server.log" | tr -d ' ')
      kill -TERM "-$PI_PID" 2>/dev/null || true
      break
    fi
    if [ "$elapsed" -ge "$timeout_seconds" ]; then
      status=stopped-timeout
      server_line_at_stop=$(wc -l <"$RUN_DIR/server.log" | tr -d ' ')
      kill -TERM "-$PI_PID" 2>/dev/null || true
      break
    fi
    sleep 5
  done

  if [ "$status" != running ]; then
    stop_checks=0
    while kill -0 "$PI_PID" 2>/dev/null && [ "$stop_checks" -lt 50 ]; do
      stop_checks=$((stop_checks + 1))
      sleep 0.1
    done
    if kill -0 "$PI_PID" 2>/dev/null; then
      kill -KILL "-$PI_PID" 2>/dev/null || true
    fi
  fi
  set +e
  wait "$PI_PID"
  pi_status=$?
  set -e
  pi_group=$PI_PID
  PI_PID=""
  if /usr/bin/pgrep -g "$pi_group" >/dev/null 2>&1; then
    kill -KILL "-$pi_group" 2>/dev/null || true
    status=stopped-process-leak
  fi
  cancellation_drain_observed=0
  if [ "$status" != completed ]; then
    # Wait for the active request's terminal metric after the client closes.
    # This is both a cancellation barrier and a per-task evidence boundary.
    if [ -n "$server_line_at_stop" ]; then
      if /usr/bin/python3 "$ROOT/scripts/wait_terminal_metric.py" \
        "$RUN_DIR/server.log" "$server_line_at_stop"; then
        cancellation_drain_observed=1
      elif [ "$status" = stopped-timeout ]; then
        # Never begin another task with an unconfirmed cancellation boundary.
        status=stopped-cancellation-drain
      fi
    fi
  fi
  end_epoch=$(date +%s)
  wall_seconds=$((end_epoch - start_epoch))
  if [ "$status" = running ]; then
    if [ "$pi_status" -eq 0 ]; then status=completed; else status=pi-failed; fi
  fi

  set +e
  "$ROOT/scripts/verify-stage-a.sh" --task "$task_id" --workspace "$workspace" >"$task_dir/verifier.json"
  verifier_status=$?
  set -e
  verifier_utility=$(jq -r '.utility' "$task_dir/verifier.json")
  if [ "$status" = completed ] && [ "$verifier_status" -eq 0 ]; then
    accepted_utility=$verifier_utility
  else
    accepted_utility=0
  fi
  tool_calls=$(jq -s '[.[] | select(.type == "tool_execution_start")] | length' "$task_dir/pi.jsonl" 2>/dev/null || echo 0)
  failed_tools=$(jq -s '[.[] | select(.type == "tool_execution_end" and .isError == true)] | length' "$task_dir/pi.jsonl" 2>/dev/null || echo 0)
  model_error_replies=$(jq -s '[.[] | select(.type == "message_end" and .message.role == "assistant" and .message.stopReason == "error")] | length' "$task_dir/pi.jsonl" 2>/dev/null || echo 0)
  server_line_after=$(wc -l <"$RUN_DIR/server.log" | tr -d ' ')
  if [ "$server_line_after" -gt "$server_line_before" ]; then
    sed -n "$((server_line_before + 1)),${server_line_after}p" "$RUN_DIR/server.log" >"$task_dir/server.log"
  else
    : >"$task_dir/server.log"
  fi
  rejected_tool_outputs=$(grep -c 'rejected tool output' "$task_dir/server.log" || true)
  normalized_tool_calls=$(grep -c 'normalized declared schema-property tags' "$task_dir/server.log" || true)
  prefix_reuse_hits=$(grep -c '\[tool-replay\] hit' "$task_dir/server.log" || true)
  salvaged_tool_prefixes=$(grep -c 'salvaged complete tool-call prefix' "$task_dir/server.log" || true)
  transcript_hash=$(shasum -a 256 "$task_dir/pi.jsonl" | awk '{print $1}')

  jq -n \
    --arg task_id "$task_id" --arg status "$status" \
    --arg transcript_sha256 "$transcript_hash" \
    --argjson pi_exit "$pi_status" --argjson verifier_exit "$verifier_status" \
    --argjson verifier_utility "$verifier_utility" --argjson utility "$accepted_utility" \
    --argjson wall_seconds "$wall_seconds" --argjson tool_calls "$tool_calls" \
    --argjson failed_tool_calls "$failed_tools" \
    --argjson model_error_replies "$model_error_replies" \
    --argjson rejected_tool_outputs "$rejected_tool_outputs" \
    --argjson normalized_tool_calls "$normalized_tool_calls" \
    --argjson prefix_reuse_hits "$prefix_reuse_hits" \
    --argjson salvaged_tool_prefixes "$salvaged_tool_prefixes" \
    --argjson cancellation_drain_observed "$cancellation_drain_observed" \
    '{task_id:$task_id,status:$status,pi_exit:$pi_exit,verifier_exit:$verifier_exit,
      verifier_utility:$verifier_utility,utility:$utility,wall_seconds:$wall_seconds,
      tool_calls:$tool_calls,failed_tool_calls:$failed_tool_calls,
      model_error_replies:$model_error_replies,
      rejected_tool_outputs:$rejected_tool_outputs,
      normalized_tool_calls:$normalized_tool_calls,prefix_reuse_hits:$prefix_reuse_hits,
      salvaged_tool_prefixes:$salvaged_tool_prefixes,
      cancellation_drain_observed:($cancellation_drain_observed == 1),
      transcript_sha256:$transcript_sha256}' >>"$RUN_DIR/results.jsonl"
  echo "task=$task_id status=$status utility=$accepted_utility wall_seconds=$wall_seconds"

  if [ "$status" = stopped-critical-pressure ] || [ "$status" = stopped-swap-growth ] \
    || [ "$status" = stopped-process-leak ] || [ "$status" = stopped-cancellation-drain ]; then
    suite_status=$status
    break
  fi
done

kill "$SERVER_PID" 2>/dev/null || true
set +e
wait "$SERVER_PID"
server_status=$?
set -e
SERVER_PID=""
final_swap=$(swap_used_mib)
suite_end_epoch=$(date +%s)
suite_wall_seconds=$((suite_end_epoch - suite_start_epoch))
peak_pressure=$(awk 'NR > 1 && $3 > peak {peak=$3} END {print peak+0}' "$RUN_DIR/pressure.tsv")
peak_swap=$(awk 'NR > 1 && $4 > peak {peak=$4} END {print peak+0}' "$RUN_DIR/pressure.tsv")
free_kib_after=$(df -k "$ROOT" | awk 'NR == 2 {print $4}')
/usr/bin/pmset -g therm >"$RUN_DIR/thermal-after.txt" 2>&1 || true

jq -s \
  --arg status "$suite_status" \
  --argjson server_exit "$server_status" \
  --argjson swap_after_mib "$final_swap" \
  --argjson swap_before_mib "$baseline_swap" \
  --argjson swap_peak_mib "$peak_swap" \
  --argjson pressure_peak "$peak_pressure" \
  --argjson suite_wall_seconds "$suite_wall_seconds" \
  --argjson free_kib_after "$free_kib_after" \
  '{status:$status,server_exit:$server_exit,tasks:.,task_count:length,
    utility:(map(.utility)|add // 0),task_wall_seconds:(map(.wall_seconds)|add // 0),
    wall_seconds:$suite_wall_seconds,
    verified_utility_per_hour:(if $suite_wall_seconds > 0
      then 3600 * (map(.utility)|add // 0) / $suite_wall_seconds else 0 end),
    swap_used_mib_before:$swap_before_mib,swap_used_mib_after:$swap_after_mib,
    swap_growth_mib:($swap_after_mib-$swap_before_mib),swap_peak_mib:$swap_peak_mib,
    pressure_peak:$pressure_peak,free_kib_after:$free_kib_after}' \
  "$RUN_DIR/results.jsonl" >"$RUN_DIR/summary.json"

shasum -a 256 "$RUN_DIR/manifest.json" "$RUN_DIR/server.log" "$RUN_DIR/pressure.tsv" \
  "$RUN_DIR/results.jsonl" "$RUN_DIR/summary.json" "$RUN_DIR/thermal-before.txt" \
  "$RUN_DIR/thermal-after.txt" "$RUN_DIR/system-prompt.txt" "$RUN_DIR/pi-models.json" >"$RUN_DIR/SHA256SUMS"
echo "run_dir=$RUN_DIR"
jq . "$RUN_DIR/summary.json"
test "$suite_status" = completed
