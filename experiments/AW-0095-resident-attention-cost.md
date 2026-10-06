# AW-0095 — Resident attention packing retains a small compute gain

## Status, hypothesis and predeclared metric

Complete diagnostic retained. Hypothesis: attention-only PQ compute gains
survive resident weights. Frozen rule before execution: warm compute PTQ/PQ>1
at every tested single-column early/middle/late layer. ABBA repeated3 per case,
first ABBA retained but excluded from warm median. Both device graphs/weights
installed once and retained, inputs fixed actual prompt values;1 and16 columns.
90s per case, pressure/swap gates. Setup durations retained in native log;
process wall includes setup. All individual timings retained, no cherry picking.

## Results and limitations

Single-column compute ratios1.125/1.077/1.096, total1.124/1.132/1.096;
16-column compute1.222/1.164/1.195, total1.217/1.156/1.189. Rule retained.
Pressure1/swap0. Both arms coexist: about15.2MB paired weight payload plus
inputs/outputs, warm repeated working set, unlike full6GB model. Cache effects
and few repetitions preclude full decode extrapolation; no25% endpoint claim.
Installation occurs once, not included in repeat compute totals; logged and
included in process walls. Output readback includes finite-value validation.
This changes cost diagnosis from AW-0094 graph-lifetime installation, rather
than reversing that result. Actual inference full working-set screen still due.

## Configuration and evidence

Fixed16GB M1 Macmini9,1/internal SSD/macOS27.0.1 build26A434; Prism runtime
adfffbe41b2cabcd51fff326ab045662265062bb and model HF revision
b072e1d3b35a0a630cece372c2127528e0994386. Actual AW-0093 inputs, full
AW-0094 exact paired attention-output weights; uncontrolled warm page/shader
cache, no thermal warnings. No generation/sampling/context/KV/vision or agent
tasks in isolated graph. Source capture context2048, FP16 KV, one sequence.
Native source/header/binary/reference/weights/runtime identities in frozen
plans and their linked evidence; no endpoint scoring or permissions changed.

## Commands and disposition

clang++ -std=c++17 -O2 with pinned AW-0084 headers, -lggml -lggml-base
-lggml-metal, absolute bundled library rpath; native binary hash in plan.
python3 scripts/check_bonsai_resident_packing_cost.py (exit0).
External /Users/chad/Models/agentwing/evidence/AW-0095; small committed
receipt evidence/AW-0095-resident-attention-cost.json. Source/raw hashes audited.
Retained for full working-set/cost/fidelity screening. No model artifact changed.
