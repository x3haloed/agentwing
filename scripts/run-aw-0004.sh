#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export AGENTWING_ACCEPT_SCHEMA_TAGS=1
export AGENTWING_EVIDENCE_ROOT="${AGENTWING_EVIDENCE_ROOT:-/Users/chad/Models/agentwing/evidence/AW-0004}"
exec "$ROOT/scripts/run-aw-0002.sh"
