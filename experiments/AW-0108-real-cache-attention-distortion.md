# AW-0108 — Real cache attention distortion screen

Hypothesis: preserving q8 K and quantizing V with the preserved Atomic Turbo
codec can survive a cheap real-attention distortion falsifier before integration.
Primary metric: relative attention-output L2 against AW-0107 independent CPU
FP16 attention over all 98304 outputs at each actual full-attention layer3/31/63.
Predeclared provisional rejection limit:0.25 at every layer. This limit is not
agent/model quality acceptance and cannot authorize promotion.

Frozen plan and hashes: `evidence/AW-0108-real-cache-distortion.json`.
Raw evidence: `/Users/chad/Models/agentwing/evidence/AW-0108` on internal SSD.
The plan records executed source, captured authority and both loaded dylib hashes.
Model/runtime/capture configuration inherits hashed AW-0106 and AW-0107; same
16-token raw prompt, F16 populated cache, 24/4 GQA, dimension256, causal masks.
Only16 populated positions are encoded; padded cells are excluded. Independent
CPU oracle was validated against native Metal attention before this screen.
Quantization uses Prism q8_0 keys and Atomic Turbo2/3/4 values, inverse WHT in two
128-element groups. Each encoded row has checked boundary canaries. This is
CPU reconstruction and attention, not registered compressed Metal cache.

| V codec | Layer3 | Layer31 | Layer63 | Disposition |
| --- | ---: | ---: | ---: | --- |
| Turbo2 | .287992 | .315103 | .268401 | Rejected by provisional screen |
| Turbo3 | .151209 | .163403 | .133528 | Retained for broader falsifiers |
| Turbo4 | .112520 | .095140 | .102356 | Retained for broader falsifiers |

Execution exit0. Phase pressure1, swap898.06MiB unchanged, macOS27.0.1/26A434.
No continuous host/performance claim; no tool calls or harness tasks in this
component test. No speed, long-context, vision, complete Google PolarQuant/QJL,
accumulated generation or general capability claim. Current runtime keeps FP16
KV; frozen P1 and all endpoint gates remain intact. Next evidence needed is
broader actual context/cache behavior and faithful runtime integration for the
survivors, then replicated end-to-end acceptance.
