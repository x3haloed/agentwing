# AW-0105 — Standalone Turbo codec builds against Prism public ABI

## Status and frozen hypothesis

Complete block-ABI smoke pass. Before build freeze complete unchanged Atomic
CPU codec, Prism public ABI headers, private Atomic common/quants/impl headers,
compiler command and acceptance: compiler0, loadable dylib, finite/deterministic
encodings with buffer bounds intact. Before smoke freeze four256-value patterns,
T2/3/4 byte sizes, two128-value WHT groups and no numeric quality threshold.

## Results

clang -std=c11 -O2 -dynamiclib, pinned public headers/base library/rpath: exit0.
One preserved extern-variable initializer warning; no warning-as-error or full
runtime build claim. Dylib loads.12 pattern/format cases, repeated twice, retain
both canaries and byte-identical encodings; all reconstructed values finite.
Two128 groups per256 head; inverse WHT applied per128, not blindly to256.
No numerical acceptance inferred: sine/Gaussian relative reconstruction errors
T2 .311/.323, T3 .171/.177, T4 .117/.122. Sparse one-hot is misleadingly easy
(~2e-5 to2.5e-4), so it cannot support no-loss claims. Zero reconstructs exactly.

## Configuration and scope

16GB M1 Macmini9,1/internal SSD/macOS27.0.1 build26A434, AppleClang21,
source Atomic074bf826e1b06005a51737d29387e36657f41bf7, MIT. Target Prism
adfffbe41b2cabcd51fff326ab045662265062bb, bundled ggml-base linkage. Both
public headers and all copied private source hashes in frozen plan. Complete
CPU codec copied unchanged, no tensor enum registration/remapping, Metal graph,
K/V cache writing, model inference, vision, sampling, agent task or endpoint.

Pressure phase samples1/swap914.06MiB unchanged; tiny smoke has no continuous
pressure or timing claim. No model-owning workload concurrent. Practical WHT/
Lloyd-Max codec; not established complete Google PolarQuant+QJL equivalence.
Standalone compatibility does not resolve AW-0104 IDs or asymmetric dispatch.

## Commands and evidence

Compiler exact argv/version in external plan; its full stdout/stderr and exit
preserved. python3 scripts/check_turbo_prism_codec_smoke.py (exit0).
External /Users/chad/Models/agentwing/evidence/AW-0105 contains immutable source,
headers/library/compiler log, build/smoke plans/result/executed checker and
recursive hashes. Small evidence/AW-0105-prism-codec-smoke.json pins receipts.
Current launcher, P1, native effort/output budgets and corpus/gates unchanged.

## Disposition

Retained for actual K/V captures and attention-output falsifiers before full
Prism registration/Metal integration. No cache quality, numeric fidelity,
performance, broad capability or25% utility improvement accepted by this smoke.
