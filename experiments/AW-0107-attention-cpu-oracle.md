# AW-0107 — Independent real masked/GQA attention oracle

## Status and predeclared experiment

Complete pass. Before execution freeze per-layer full-output relative L2<=1e-3,
finite active Q/K/V/output, and wrong KV-head rotation must fail. Trust threshold
is for CPU/native oracle agreement, not lossy-cache numeric acceptance.

## Results

All294912 output values compared: L2 early7.218e-5, middle3.243e-4,
late2.815e-5. Deliberate KV-head misalignment gives1.387/1.350/1.371 and is
rejected. Double math.fsum dot/softmax/weighted-V oracle respects recorded
strides, GQA head quotient6 and actual FP16 causal mask. Each query unmasked
keys exactly0..query_index; padded/inactive cells excluded. All active inputs
and native outputs finite. This validates the authority before lossy codecs.
Host phase samples1/swap914.06MiB unchanged, no continuous/timing claim.

## Configuration and provenance

16GB M1 Macmini9,1/internal SSD/macOS27.0.1 build26A434; Prism native runtime
adfffbe41b2cabcd51fff326ab045662265062bb. Original PTQ model HF revision
b072e1d3b35a0a630cece372c2127528e0994386, SHA
53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3.
Raw iterator prompt,16 tokens, context2048, batch/ubatch128, one sequence,
rollback0 and FP16 K/V; no chat template/sampling/generation/vision or agent
benchmark. Uncontrolled warm page/shader cache, no thermal warning at capture.
No P1/profile/task/verifier/timeout/permission/scoring change. Native build
clang++ -std=c++17 -O2, pinned AW-0093 headers and bundled llama/ggml/base
libraries with absolute rpath. Exact source/binary/library identities in plan.

## Commands and evidence

python3 scripts/check_bonsai_attention_oracle.py (exit0).
External /Users/chad/Models/agentwing/evidence/AW-0107 has frozen plan, result,
executed checker and recursive receipt; capture file hashes rechecked against
AW-0106. Small evidence/AW-0107-attention-cpu-oracle.json pins exact hashes.

## Disposition

Retain oracle for q8-K/Turbo-V accuracy screen. Actual prompt is short, no
long-context/rare-prompt, Metal compressed-cache, candidate accumulation,
general capability or utility/hour evidence. Original runtime still FP16.
