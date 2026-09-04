#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PI_STATE="$ROOT/var/pi-agent"
NODE_BIN="${AGENTWING_NODE_BIN:-/Users/chad/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node}"
MODELS_FILE="${AGENTWING_PI_MODELS_FILE:-$ROOT/config/pi-models.json}"

mkdir -p "$PI_STATE"
cp "$MODELS_FILE" "$PI_STATE/models.json"

export PI_CODING_AGENT_DIR="$PI_STATE"
exec "$NODE_BIN" "$ROOT/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js" \
  --provider agentwing-swiftlet \
  --model qwen3.6-35b-a3b-8bit-qpack \
  "$@"
