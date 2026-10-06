# AW-0140 — Turbo full multimodal native/Pi functional admission

## Status and predeclared hypothesis

Completed two fresh-server replicates. Same functional gates as AW-0099: text42,
reversed red/blue image halves, native lookup tool selection/result association,
Pi exact file copy and verification, existing host/protocol gates. This is a
functional falsifier, not endpoint utility or held-out capability qualification.

## Frozen conditions

`evidence/AW-0140-multimodal-plan.json` freezes all runtime/spec/launcher/harness/
Pi adapter/provider/boundary hashes, request sampler and reasoning, OS/hardware/
thermal/storage/cache policy and deadlines. New experimental server16K/q8 K/
Turbo4 V/flashON/full unchanged Q8 vision1024/no-shift/cacheRAM0/checkpoints2,
T1/top_p.95/top_k20/min_p.05/presence0/repeat1/medium. Native request cap768
matches previous functional fixture; Pi retains full8192 output/16K context.
Diagnostic `--verbose` recorded; no task-set/verifier/permission policy changes.
Original P1/default launcher preserved. Internal SSD M1/16GB/macOS27.0.1.

## Execution

`python3 scripts/probe_bonsai_turbo_local.py`, two replicates, startup180s,
replicate1800s/Pi900s, continuous host monitoring and stop on first failure.
Raw evidence `/Users/chad/Models/agentwing/evidence/AW-0140`.
Independent replay via `scripts/audit_bonsai_turbo_admission.py` once both end.

## Results and disposition

Both replicates and independent replay passed. Walls were 156.744 and 181.104
seconds; pressure peaked at level1 and swap growth was zero in both. Existing
swap at baseline was 1196.12MiB. All text, reversed image ordering, native lookup
and tool-result association, and exact Pi file-copy gates passed. The campaign
had 16 terminal serialized server requests and eight valid productive tool
attempts (two native, six Pi), with zero redundant, malformed, denied or failed
calls. Pi byte/newline inspection served a distinct purpose from text reading.

`evidence/AW-0140-turbo-multimodal-admission.json` records raw run/result hashes,
independent audit hash, protocol pins and complete accounting. Per-run external
`sha256.json` manifests were independently replayed. Raw traces remain outside
Git. The frozen plan SHA is
`69f27bb2b5ee8a7188b2258947092265c9c0ea334c2704c282fc7a42766d8a91`.

Retain the experimental launcher with machine-readable functional admission.
These small fixtures do not establish occupied long-context fidelity, unfamiliar
repository capability, or the required 25% utility gain. Timings are unpaired
and not an FP16/P1 performance comparison. No default or P1 promotion.
