# AW-0123 — Remapped Turbo codec registration build

## Status and hypothesis

Retained integration stage. Register remapped Turbo cache types and unchanged
Atomic KV CPU codec routines in pinned Prism GGML base without requiring
unrelated Atomic weight formats or changing Prism existing type identities.

## Configuration and reproduction

Prismadfffbe exact source baseline, separate codex/turbo-cache source worktree
`/Users/chad/Models/agentwing/runtime-sources/prism-turbo-port`, original baseline
checkout/build untouched. Atomic074bf826e1b06005a51737d29387e36657f41bf7 public
MIT source. Extract its contiguous KV codec prefix before unrelated TQ3_1S/TQ4_1S
weight section; KV routines unchanged. DefaultTurbo4 four-bit branch retained,
not full Google equivalence claim. Types144/145/146,COUNT147; original42/142/143
preserved. Add block definitions/prototypes/type traits and source build entry.
No Metal dispatch/op/cache-graph adaptation yet.

Frozen full patch `experiments/runtime-patches/AW-0123-turbo-codec-registration.patch`
applies cleanly to unmodified exact Prism baseline (`git apply --check` passes).
Plan includes patch/harness hashes, complete argv/compiler/tool/host/source pins.
Build CMake3.31.6/Ninja1.11.1.4 Release embedded Metal,targetllama,parallel2;
isolated output `/Users/chad/Models/agentwing/runtime-builds/prism-turbo-codec`.
`python3 scripts/build_prism_turbo_codec.py` exit0.

## Acceptance and results

Predeclared build-only rule: configure/build exits0,nonempty runtime libraries,
host pressure<4/swap growth<=1024MiB;600s/phase watchdog,.5s sampling.
Both exit0,configure3.085s/build71.031s,pressure1/swap growth0. Existing known
extern-initializer warning retained, no Werror-clean claim. Exact dylibs hashed.
M1 Macmini9,1/16GB/internal SSD/macOS27.0.1/26A434/Apple Clang21. No model
inference, sampling, harness task/tool/verifier/permission changes.

## Evidence and disposition

`evidence/AW-0123-turbo-registration.json`; raw logs/host samples/patch at
`/Users/chad/Models/agentwing/evidence/AW-0123`. Retain remapped base registration
for AW-0124 and backend/cache integration. No CPU attention backend, Metal cache
graph/model generation, vision or endpoint acceptance. Failed AW-0122 preserved.
