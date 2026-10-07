# AW-0222 — Bounded generation checkpoint screen

Prepared/unbuilt/unqualified. Opt-in patch `patches/AW-0222-generation-checkpoints.patch` saves synchronized ordinary non-speculative RS state every512generated tokens, prior to pending sampled token; existing two-checkpoint memory bound retained. Original runtime/source/defaults untouched. Pins/scope/gates in `evidence/AW-0222-generation-checkpoint-preparation.json`.

Hypothesis: later recurrent checkpoints preserve exact-prefix continuation and reduce complete capture+replay cost. First build isolated source; use own deterministic512/1024/1536token histories and prefix suffix boundaries before/at/after saved positions. Require finite full-logit comparison to fresh replay under predeclared numerical tolerance before any utility run. Freeze actual executable identities/fixture bytes/tolerance before launch. Then >=2 interleaved capture+replay pairs, same prompts/history/sampling/context/permissions; wallcandidate<=control, pressure<4/swapgrowth<=1024MiB/disk>=8GiB/singleownerloopback. Charge all captures and failures. No task/reasoning truncation.

AW221 log/source supports opportunity, not correctness. Unresolved; fixed complete task and full interleaved P1 qualification still required.
