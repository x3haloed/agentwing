# AW-0136 — Actual generation under compressed model cache

## Status and hypothesis

Retained bounded functional pass. Unlike posthoc FP16-generated cache screens,
this probe actually generates its own32 tokens with newly integrated q8 K and
Turbo4 V model cache, native Metal writer/attention/inverse graph.

## Frozen configuration and primary acceptance

Plan pins executed source/harness/binary/model, newly built AW-0135 runtime
libraries and actual compiled source headers. Explicit backend directory and
rpath point to isolated new runtime. Selective Bonsai artifact SHA
cc11a9c76ee8e94a735e14789e17b952b33c9b84e7fe587b40dfe6cd6b96566c;
Prismadfffbe plus full archived AW-0135 patch/Atomic074bf826 lineage, MIT.
Internal SSD M1 Macmini9,1/16GB/macOS27.0.1/26A434.

Same raw16-token iterator prompt as prior probe; context2048/batch128,one sequence,
no rollback sequences, flash attention explicitly enabled, Kq8_0/Vturbo4.
Native sampler T1/top_p.95/top_k20/min_p.05/repeat1/presence0/frequency0/seed42.
Raw template, no medium chat-effort claim. Exact32-token requirement; captures
complete attention-out/FFN-down inputs/outputs at layers0/31/63 for prompt and
each generated forward (six nodes per forward), full vocabulary logits per
sampling step.64MiB activation cap in native source;120s watchdog,.25s host
pressure/swap checks, one advisory owner. No tools/task/verifier changes.

Primary predeclared acceptance: native exit0,32 generated forwards,198 selected
nodes/396 complete finite F32 activation files,32 full finite vocabulary-logit
rows and host gates. Numeric FP16 comparison diagnostic only, no new posthoc
numeric threshold or endpoint-quality acceptance.

`python3 scripts/capture_bonsai_turbo_generation.py` exit0;
`python3 scripts/audit_bonsai_turbo_generation.py` independently passes.

## Results

Runtime confirms2048 cells/16 full-attention layers: q8 K34MiB + Turbo4 V17MiB
=51MiB KV allocation, versus observed128MiB in same-context FP16 AW-0109.
77MiB/60.15625% KV allocation reduction; excludes weights/recurrent state/scratch,
checkpoints/vision/total process RSS, and is not a speed claim or16K measurement.

Actual generated32 token IDs match frozen FP16 probe exactly. All396 complete
activation files contain4,866,048 finite values;32 full248320-vocabulary rows
contain7,946,240 finite logits. Independent audited reference hashes match
AW-0098 selective FP16 arm; no teacher forcing. Numeric change remains:
max selected activation relative L2 .2910596 (late attention-out input), max
logits-row relative L2 .0501940. These diagnostics caution against inferring
general quality from identical short token sequence. No inherited exact-format
1e-3 fidelity rule is applied to this lossy representation.

Pressure peak1/swap growth0, no thermal warning reported. Generated text and
all traces remain outside Git; small manifest/summary/hashes committed.

## Evidence and disposition

`evidence/AW-0136-turbo-model.json`; raw native logs/generated text/complete
activations/logits/independent audit/source copies at
`/Users/chad/Models/agentwing/evidence/AW-0136`.
Retain actual compressed-cache model path for broader evaluation. This is one
short raw probe, not server/vision/tool-protocol/long-context/general capability,
end-to-end work-rate or promotion evidence. Existing P1/active launcher intact.
Next: broaden generation/context and vision/server admission, then frozen
independent task verifiers and replicated interleaved endpoint comparisons.
