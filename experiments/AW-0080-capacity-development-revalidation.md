# AW-0080 — Larger-capacity development revalidation

## Status and hypothesis

Running; frozen before launch. The retained 16K context / 8192 output medium-thinking
profile may resolve AW-0072 capacity failures across all eight development
tasks while preserving host, protocol, permission and history gates.

## Fixed conditions and identities

Configuration: `spec/bonsai-capacity-candidate.json`, pinned PTQ1_0 language
and Q8 vision, Prism adfffbe runtime, full local vision stack, internal SSD,
16 GB M1 Mac mini. Frozen plan `evidence/AW-0080-development-plan.json`
SHA-256 `e129d35e09e27c0a5be9605b5c99b50721d7380c8c2caa946210ebed9768f6d5`
pins runner, canonical bounded-bash-v2 checker, model configuration, prompt,
permissions, task and verifier inputs. T1 / p.95 / k20 / min_p.05 /
presence0 / repeat1; medium reasoning. No context shift or compaction,
archive0, checkpoint2, FP16 KV. 1800 seconds per task, fresh model per task;
OS page cache uncontrolled. Record actual OS, thermal and free-space state
on launch. Sealed held-out tasks remain unexposed.

## Primary metric and cheap falsifier

Require independent utility1 for all eight selected development tasks and
all host/protocol/history gates. Semantic failures remain charged and allow
later tasks; protocol, history or host failure stops the screen. Startup,
artifact verification, client, tools and independent grading are charged;
final recursive receipt creation is outside this diagnostic timing. No
promotion-rate claim. AW-0078 must first finish and pass independent audit.

## Commands and validation

`python3 scripts/run_bonsai_capacity_development.py --freeze`.
Recomputed every frozen source/input hash successfully; exactly eight
pre-existing development tasks, unchanged authority and 1800s deadline.
Updated independent auditor chooses the canonical safe checker only for
plans explicitly declaring bounded-bash-v2. Replayed AW-0076 through that
auditor: audit and diagnostic passed. No old plan or trace changed.
Before inference, use runner `--check-only` once no other model owner remains.

## Evidence and disposition

Run evidence pending under `/Users/chad/Models/agentwing/evidence/AW-0080/`;
runner snapshots all pinned sources and emits recursive raw hashes.
Retained as a frozen conditional experiment, not promoted or qualified.
Expanded capability, held-out and replicated interleaved endpoint gates
remain open; native P1 versus Bonsai matching policy remains unresolved.

## Launch update

Launched after AW-0078 terminal independent audit passed 8/8 original tasks.
Preflight and every frozen source/input hash passed before launch. External
run `/Users/chad/Models/agentwing/evidence/AW-0080/20261006T053829.945708Z`; all 225 pinned source/input snapshots verified against
the frozen plan. Manifest hash and actual host/OS/cache/thermal/storage state
are preserved in `evidence/AW-0080-launch-check.json`. Results pending.
No concurrent model owner or model download started.

Confounder retained: AW-0081 source-derived integer layout check ran for
approximately 2.1s during navigation. Its CPU work remains inside task wall;
AW-0080 is an unpaired diagnostic, not a clean comparative rate measurement.
