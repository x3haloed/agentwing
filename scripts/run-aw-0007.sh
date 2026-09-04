#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export AGENTWING_EVIDENCE_ROOT="${AGENTWING_EVIDENCE_ROOT:-/Users/chad/Models/agentwing/evidence/AW-0007}"
exec "$ROOT/scripts/run-aw-0004.sh"
