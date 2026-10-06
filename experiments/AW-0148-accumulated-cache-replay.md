# AW-0148 — accumulated-prefix cache fidelity replay

Completed; independent numeric audit passes. AW-0146 schema and AW-0147 executable-mode
setup failures preserved. Same compiled fixture uses pinned full-server language
libraries, selective artifact,16K context/batch128/flashON, identical saved prompt
bytes and native sampler/seed42. FP16 K/V versus q8-K/Turbo4-V only. Fresh process
per arm; pair order alternates across0/1024/4096/7695 thinking-chunk checkpoints.
Chunk counts are not tokenizer positions. Language-only diagnostic; projector
not used here. Prior full vision functional evidence remains AW-0140.

Plan freezes first-row full-logit relative L2<=0.10 and top20 overlap>=0.50,
identical prompt-token bytes, full finite logits and32 own generated tokens,
exit0, pressure<4, swap growth<=1024MiB,600s per arm. These are provisional
technical falsification gates, not broad quality or endpoint promotion. Subsequent
own-trajectory differences are descriptive: different generated inputs cannot
support equal-prefix numeric comparisons. Selected early/middle/late projection
activations captured during own32 decode; prefill capture disabled to bound traces.

Command python3 scripts/run_bonsai_accumulated_cache_replay_v3.py. Plan copy:
evidence/AW-0148-cache-replay-plan.json. Raw/source/binary/headers/compiler/runtime/
model/hardware/OS/storage/cache/thermal hashes at
/Users/chad/Models/agentwing/evidence/AW-0148. Large logits/activations outside Git.
Native tokenization declared identically in both arms; no exact server KV-history
claim. AW-0145 verifies rendered base bytes. No rescoring failed AW-0141, reduced
agent reasoning budget, altered benchmark, utility comparison or promotion.

## Interim independent replay

First0-chunk pair completed and passes:1186 identical input tokens; first-row
relative logit L2 .0437951, top20 overlap1.0, own32tokenIDs all32match. Hashes,
headers/libraries/input pins,384 selected activation files and32whole-logit rows
finite, host gates replayed. Full four-checkpoint verdict remains pending; the
ongoing arm is1024-chunk Turbo. These are diagnostic results, not endpoint rates.
Auditor: scripts/audit_bonsai_accumulated_cache_replay.py --partial; interim raw
audit outside Git at external AW-0148/partial-audit.json.

Second1024-chunk pair also passes provisional numeric gates:2210 identical
input tokens, first-row L2 .0416344 and top20 overlap .95. Own32 sampled IDs
match at25 positions; common prefix reported by updated auditor to distinguish
shared history from later coincidental matches. Longer4096/7695 pairs pending.
This weakens any extrapolation of short-prompt token identity to general behavior;
no endpoint/general-quality acceptance or causal timeout attribution.

## Final disposition

Eight arms exit0; all raw hashes/shapes/finite logits/activations, exact input-token
bytes, allocator formats, pinned headers/libs/inputs and execution-summary replay
pass. Four prefixes have1186/2210/5282/8881tokens. First-row logit relative L2
.043795/.041634/.024844/.052939; top20 overlap1/.95/1/1. Own32 common sampled
prefix lengths32/22/12/9, total matching positions32/25/12/9. Pressure1 and zero
swap growth throughout. Gate passes, but sampled behavior is not invariant.

Seal evidence/AW-0148-cache-replay-terminal.json; raw final-audit.json and
execution-summary.json hashes recorded. Retain numeric survivor only. No general
capability or25% utility proof, no causal attribution of AW141 failure to cache,
no promotion. Next exact accumulated-prefix full request comparison can determine
whether long generation persists under both formats; frozen task failure remains.
