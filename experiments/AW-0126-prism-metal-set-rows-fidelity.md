# AW-0126 — Integrated Prism Metal SET_ROWS fidelity

## Status and hypothesis

Retained. Registered Prism Metal backend can execute ggml_set_rows for new
Turbo3/4 destinations and reproduce previously validated native writer outputs
byte-exactly on actual populated Bonsai V rows at layers3/31/63.

## Configuration and acceptance

Frozen plan hashes newly built AW-0125 authority, all runtime dylibs, native
probe/source/harness and AW-0117 real input/output authority. Uses source-built
Prism backend, allocation and graph computation APIs, not direct Swift kernel
invocation. Backend supports-op must return true before graph execution. Destination
256×192, F32 source same shape, i64 indices191..0. Type IDs145/146 inherited
remapped registration. Actual runtime picks pipeline and threads/arguments.
No rewriting prepared kernel dispatch to make it pass.

Primary rule: six actual graphs supported,exit0 and packed outputs byte-identical
to AW-0117 GPU writer (which has independent CPU/canary checks).90s/case timeout,
.25s host checks and external host series. Compile with pinned source GGML headers,
link built ggml/base/Metal with explicit isolated rpath. Internal SSD M1 Macmini9,1/
16GB/macOS27.0.1; model/capture provenance AW-0109. No new model inference,
harness task/verifier, sampling, tools or permissions.

`python3 scripts/check_prism_turbo_metal_writer.py` exit0.

## Results and evidence

All six graphs supported/exits0; every packed output byte-identical to AW-0117
native authority.192 populated rows per case, no inactive padding input. Peak
pressure1/swap growth0. Native logs record actual newly integrated pipeline
selection/runtime compilation. No model quality or performance claim.

`evidence/AW-0126-prism-metal-writer.json`; raw source/probe/logs/captures/host
series `/Users/chad/Models/agentwing/evidence/AW-0126`.

## Disposition and limits

Retain actual Prism Metal writer registration/dispatch. Compressing model cache
requires attention specialization and inverse op/cache graph wiring, verified
allocations and accumulated compressed generation; these remain outstanding.
No server/vision/endpoint qualification, no change to admitted launcher or P1.
