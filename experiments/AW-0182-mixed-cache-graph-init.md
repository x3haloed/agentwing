# AW-0182 — narrow graph guard and full16K admission

AW181 failed on remaining model-graph Q8K assertion, despite AW180 kernel
integrity. Hypothesis: admit only validated F16K/Turbo4V256-wide heads while
preserving prior q8/Turbo3-or4 path; full context initialization then succeeds.
Isolated new source/build, patch series AW137/AW179/AW182 atop adfffbe.
Symmetric inherited source comparison3531files, only llama-graph.cpp changes
from AW179. Release/embeddedMetal/OpenSSLoff explicit pinned CMake/Ninja,
llama+ggml-metal269steps -j4 exit0. Full library/source/config hashes recorded.

Before expensive fullprefix runs, new native fixture loads same selective model,
ctx16384/batch128/RS0/flashon/one sequence and F16K/Turbo4V; context graph
reservation only, no tokens decoded or tools/vision encoded. Owner lock,
90s watchdog/pressure<4/swapgrowth<=1024MiB. Exit0 CONTEXT_INIT_OK in5.101s,
KV648MiB (F16K512+Turbo4V136), pressure1/growth0 baseline1071.12MiB.
Independent raw/source/binary/host replay passes. This is an allocator/graph
admission result, not numeric generation or full model quality acceptance.

InternalSSD16GBM1, OS/hardware/thermal/model/fullparentprofile/runtime/source /
patch/compiler/library/cache provenance in plan and receipt. No performance
ratio or endpoint utility assigned. Original P1/default/runtime untouched.
Retain admission survivor; next repeat same-runtime four-arm late-prefix test
before full tool/vision/endpoints. Earlier AW179/AW181 failures preserved.

Reproduce pinned external configure/build logs; compile
experiments/fixtures/bonsai-mixed-context-init.cpp against candidate libraries;
python3 scripts/check_bonsai_mixed_context_init.py (refuses completed overwrite).
Raw: /Users/chad/Models/agentwing/evidence/AW-0182.
Manifest: evidence/AW-0182-mixed-cache-graph-init.json.
