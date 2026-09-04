#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DEPS="$ROOT/spec/dependencies.json"

swiftlet_path=$(jq -r '.swiftlet.local_path' "$DEPS")
swiftlet_want=$(jq -r '.swiftlet.revision' "$DEPS")
model_path=$(jq -r '.qwen3_6_35b_a3b_8bit_qpack.local_path' "$DEPS")
model_hash_want=$(jq -r '.qwen3_6_35b_a3b_8bit_qpack.hash_manifest_sha256' "$DEPS")

test -d "$model_path"
test -f "$model_path/manifest.json"
test -x "$swiftlet_path/.build/release/swiftlet"
test -x "$swiftlet_path/.build/release/swiftlet-server"

swiftlet_got=$(git -C "$swiftlet_path" rev-parse HEAD)
test "$swiftlet_got" = "$swiftlet_want"
model_hash_got=$(shasum -a 256 "$model_path/hashes.json" | awk '{print $1}')
test "$model_hash_got" = "$model_hash_want"

echo "Agentwing dependency check: PASS"
echo "Swiftlet: $swiftlet_got"
echo "Model hash manifest: $model_hash_got"
memory_pressure -Q
sysctl vm.swapusage
