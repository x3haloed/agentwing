# AW-0094 — Broaden packing cost screen to attention-output and FFN-down

## Status and predeclared experiment

Complete diagnostic. Freeze exact tensor selection before extraction and freeze
cost plan before native benchmark: AW-0092 ABBA repeated3 times per case,
1/16 real input columns, first ABBA retained warmup excluded from steady median,
90s per case, host gates. Retain for further screening if any warm total PTQ/PQ
ratio>1; never an endpoint promotion rule. Twelve cases completed.

## Results

| Family | Columns | Total PTQ/PQ early/middle/late | Compute PTQ/PQ early/middle/late |
|---|---|---|---|
| Attention output | 1 | .964/.909/.921 | 1.103/1.039/1.068 |
| FFN-down | 1 | .845/.842/.762 | .855/.835/.675 |
| Attention output | 16 | 1.068/1.097/1.107 | 1.167/1.195/1.204 |
| FFN-down | 16 | 1.109/1.104/1.099 | 1.214/1.239/1.212 |

Total includes metadata/device allocation, weight/input transfer, synchronous
compute, output readback and cleanup. Process wall (including backend startup)
and every trial retained separately. Attention resident compute gain is modest;
extra installation erases it in this graph-lifetime test. PQ FFN-down single
column compute is slower at all sampled layers. Prefill16 improves both.
All outputs finite, no fidelity comparison performed by cost probe.

## Representation and preparation costs

Full6144x5120 attention tensor6,881,280→8,355,840 bytes;
17408x5120 FFN-down19,496,960→23,674,880 bytes. Bounded native exact converter
uses original scale/code-preserving AW-0086 library (hash verified), no full
artifact conversion. Per-tensor warm read, allocation/conversion and write
seconds retained. Full source file SHA verified using8MiB streaming chunks.
Conversions and writes are warm buffered operations without fsync; those write
times do not establish durable install/cold storage performance. Whole-model
or full6–7GB working-set effects and peak residency remain unmeasured. Native
benchmark retains both host fixture formats but one active device graph.

Host phase samples during preparation and continuous samples during native
runs were pressure1/swap0. Preparation has phase-only sampling; no continuous
pressure claim for hashing/conversion. Native all twelve cases gated normally.
No timing extrapolation to agent endpoint, full decode or installation.

## Fixed configuration and provenance

16GB M1 Macmini9,1, internal SSD, macOS27.0.1 build26A434. Runtime Prism
adfffbe41b2cabcd51fff326ab045662265062bb; model HF revision
b072e1d3b35a0a630cece372c2127528e0994386, PTQ1_0 SHA
53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3.
Uncontrolled warm OS page/shader cache; no thermal warning observed. Exact
source/model/header/native binary/runtime dylib pins in external frozen plans.
Native build clang++ -std=c++17 -O2 with pinned headers, bundled dylibs and
absolute rpath. Neither P1 nor task/verifier/reasoning/timeout/permissions/scoring
was changed. No agent endpoint utility or general capability claim.

## Commands and evidence

python3 scripts/check_bonsai_other_projection_cost.py (exit0).
External /Users/chad/Models/agentwing/evidence/AW-0094 holds preparation plan,
source/weights hashes, raw fixtures, component preparation times, full benchmark
plan/timings/native logs/host samples/result and recursive receipt.
Small evidence/AW-0094-other-projection-cost.json pins exact external hashes.
Frozen source/runtime verified after execution. No weights or large trace in Git.

## Disposition

Retained under predeclared rule for resident/selective-packing screening because
16-column cases improve. Do not integrate uniform PQ from these results;
FFN-up/down decode losses and1.173GiB uniform expansion are adverse evidence.
Selective attention packing is a possibility, not a validated successor.
Generated-token/accumulated behavior and all endpoint gates remain open.
