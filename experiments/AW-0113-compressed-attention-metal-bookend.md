# AW-0113 — Compressed attention Metal bookend

## Status and hypothesis

Retained. Applying unchanged upstream Metal inverse WHT after weighted
compressed attention reproduces independent per-row reconstructed-value
attention for actual candidate-generated captures at layers3/31/63, Turbo3/4.

## Configuration and primary acceptance

Frozen external plan records executing source, AW-0109 real capture authority,
AW-0110 packed authority, AW-0112 Metal authority, actual executable/source,
Atomic CPU codec and Prism base dylib hashes. Model/runtime/configuration pins
inherit AW-0109: selective PQ representation, original Prism runtime, FP16
cache trajectory generated32 tokens after16-token prompt, native sampler,
internal SSD M1 Macmini9,1/16GB/macOS27.0.1/26A434. No new model inference,
chat effort, task/verifier, tool or permission changes. Active48 keys, dimension256,
24/4 GQA, causal mask, q8 K, Turbo3/4 V, two128 inverse groups per head.

Predeclared rules: CPU aggregate-then-inverse versus independently
inverse-each-row-then-aggregate relative L2<=1e-6; unchanged native Metal inverse
versus per-row authority<=.005; missing-inverse negative>.25; finite outputs.
These are transform execution checks, not model-quality acceptance.

## Commands and results

`python3 scripts/check_turbo_attention_bookend.py` exit0. Six complete cases,
6144 outputs each: CPU identity error8.93e-8–1.10e-7; Metal error
.0006154–.0006643. Missing-inverse negative1.4126–1.4336 caught in all cases.
Packed V hashes match frozen AW-0110 authority. All outputs finite. Phase
pressure1/swap898.06MiB unchanged. No continuous-pressure or performance claim.

## Evidence and disposition

`evidence/AW-0113-attention-metal-bookend.json` records raw file hashes;
external `/Users/chad/Models/agentwing/evidence/AW-0113`.
Retain actual weighted-output inverse bookend, extending AW-0112 row-only
coverage. CPU computes attention; only inverse dispatch runs on GPU. Actual
compressed GPU attention, registered Prism types and cache allocation,
accumulated compressed trajectory, longer/rare contexts, vision and endpoint
campaign remain unverified. No promotion; frozen P1/current FP16 cache intact.
