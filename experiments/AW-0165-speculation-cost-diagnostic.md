# AW-0165 — observed speculative iteration cost

Retrospective diagnosis of immutable AW162 full-request failure, not a new
performance comparison or preregistered endpoint result. Primary descriptive
metric: marker-to-next-marker time divided by actual prompt-position advancement.
Verify native log hash against its terminal receipt; pair every closed speculative
window with its accepted-count/new-position record, and verify ordinary windows
advance exactly one token. No context shifts/restores; monotonic positions.
Whole model/runtime/harness/sampling/host/OS/storage/cache/thermal identity inherits
hashed AW162 plan, preserved timeout and all raw evidence.

4604 closed windows cover6399 output steps; last open window excluded. Context
bins chosen posthoc: early<2304, middle<5000, late>=5000. Single/speculative
seconds per output step are .184/.290, .199/.348, .220/.319 respectively.
These windows include decode, sampling, streaming, lookup and queue work.
Different histories and endogenous draft selection prevent causal attribution;
these are not kernel timings or configuration/endpoint speed ratios. Native
acceptance records agree with position changes; no duplicated-count correction
is warranted. Pipeline compilation is not an invocation counter.

Deprioritize unchanged ngram2/3 as presumed acceleration: observed accepted
output does not amortize its execution windows on this failed trajectory.
Keep all numeric/startup successes and negatives. Next screen the cost of actual
single-token PTQ execution before another integration or model download. P1 and
active defaults unchanged; no promotion or utility claim.

Reproduce: python3 scripts/diagnose_bonsai_speculation_cost.py.
Large per-window evidence: /Users/chad/Models/agentwing/evidence/AW-0165.
Report/source/parent/log hashes: evidence/AW-0165-speculation-cost-diagnostic.json.
